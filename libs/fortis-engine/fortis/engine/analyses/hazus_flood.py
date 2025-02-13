import numpy as np
import pandas as pd
import geopandas as gpd
from fortis.engine.models.abstract_building_points import AbstractBuildingPoints
from fortis.engine.models.abstract_flood_depth_grid import AbstractFloodDepthGrid
from fortis.engine.vulnerability.abstract_vulnerability_function import AbstractVulnerabilityFunction

try:
    # Python 3.9+
    import importlib.resources as resources
except ImportError:
    # For earlier versions, install importlib_resources
    import importlib_resources as resources


class HazusFloodAnalysis:
    def __init__(
        self,
        buildings: AbstractBuildingPoints,
        vulnerability_func: AbstractVulnerabilityFunction,
        depth_grid: AbstractFloodDepthGrid,
    ):
        """
        Initializes a HazusFloodAnalysis object.

        Args:
            buildings (BuildingPoints): BuildingPoints object.
            vulnerability_func (VulnerabilityFunction): VulnerabilityFunction object.
            hazard (Hazard): Hazard object.
        """
        self.buildings = buildings
        self.vulnerability_func = vulnerability_func
        self.depth_grid = depth_grid

        with (
            resources.files("fortis.data")
            .joinpath("flDebris.csv")
            .open("r", encoding="utf-8-sig") as debris_file
        ):
            self.debris = pd.read_csv(debris_file)
        with (
            resources.files("fortis.data")
            .joinpath("flRsFnGBS.csv")
            .open("r", encoding="utf-8-sig") as restoration_file
        ):
            self.restoration = pd.read_csv(restoration_file)

    def calculate_losses(self):
        """
        Calculates risk for each building.

        Returns:
            pandas.DataFrame or geopandas.GeoDataFrame: Building data with risk metrics.
        """
        # Required fields according to FAST
        # Area
        # Building Cost
        # (Content Cost can be computed if not provided)
        # First floor height
        # Foundation Type (according to Hazus but is basically around basement or no)
        # Lat, Lon, Point geometry
        # Number of stories
        # Occupancy class

        gdf: gpd.GeoDataFrame = self.buildings.gdf
        fields = self.buildings.fields

        # Apply the depth grid to the buildings
        gdf[fields.flood_depth] = self.depth_grid.get_depth_vectorized(gdf.geometry)

        # From the flooded depth based on other attributes determine the depth in structure.
        gdf[fields.depth_in_structure] = (
            gdf[fields.flood_depth] - gdf[fields.first_floor_height]
        )

        # Apply the vulnerability function to the buildings
        self.vulnerability_func.apply_damage_percentages()

        # Do the loss calculations
        gdf[fields.building_loss] = (
            gdf[fields.building_damage_percent] / 100.0 * gdf[fields.building_cost]
        )
        gdf[fields.content_loss] = (
            gdf[fields.content_damage_percent] / 100.0 * gdf[fields.content_cost]
        )

        # Using an inline conditional to get a column or supply a default Series:
        inventory_cost_series = (
            gdf[fields.inventory_cost]
            if fields.inventory_cost in gdf.columns
            else pd.Series(0, index=gdf.index)
        )

        if fields.inventory_damage_percent in gdf.columns:
            gdf[fields.inventory_loss] = (
                gdf[fields.inventory_damage_percent] / 100.0 * inventory_cost_series
            )

        
        # Debris
        self._vectorized_debris_calculation()
        #self._calculate_debris_inplace(self.debris)
        """
        weights = gdf.apply(
            lambda row: self.lookup_debris_weights(
                row[fields.flood_depth],
                row[fields.occupancy_type],
                row[fields.foundation_type],
            ),
            axis=1,
        )
        # Append the new columns
        gdf = gdf.join(weights)

        # Calculate the debris based on the weights
        gdf[fields.debris_finish] = gdf[fields.area] * gdf["FinishWt"] / 1000
        gdf[fields.debris_foundation] = gdf[fields.area] * gdf["FoundationWt"] / 1000
        gdf[fields.debris_structure] = gdf[fields.area] * gdf["StructureWt"] / 1000
        gdf[fields.debris_total] = (
            gdf[fields.debris_finish]
            + gdf[fields.debris_foundation]
            + gdf[fields.debris_structure]
        )

        
        # Restoration Time
        restoration = gdf.apply(
            lambda row: self.lookup_restoration_time(
                row[fields.flood_depth], row[fields.occupancy_type]
            ),
            axis=1,
        )
        gdf = gdf.join(restoration)
        """


    def _vectorized_debris_calculation(self):
        gdf = self.buildings.gdf
        fields = self.buildings.fields
        lookup_df = self.debris
    
        # 1. Create the combined key.
        lookup_df['merge_key'] = lookup_df['SOccup'] + '_' + lookup_df['FoundType']

        # 2. Create the IntervalIndex.  This is the key step.
        lookup_df['Interval'] = lookup_df.apply(lambda row: pd.Interval(row['MinFloodDepth'], row['MaxFloodDepth'], closed='left'), axis=1)

        # Set 'MinFloodDepth' as a temporary index for efficient lookup later
        lookup_df = lookup_df.set_index('MinFloodDepth')

        # 3. Group by the combined key and create a *nested* index.
        lookup_df = lookup_df.groupby('merge_key')[['Interval', 'FinishWt', 'StructureWt', 'FoundationWt']].apply(
                lambda x: x.set_index('Interval'))

        # Now create the Interval Index.
        lookup_df = lookup_df.reset_index()
        lookup_df['IntervalIndex'] = pd.IntervalIndex(lookup_df['Interval'])
        lookup_df = lookup_df.set_index('merge_key')


        # 1. Foundation Type Mapping (still in-place, as it's efficient)
        gdf['FoundType'] = gdf[fields.foundation_type].map(
            lambda x: 'Slab' if x in (6, 7) else ('Footing' if 1 <= x <= 5 else None)
        )

        # --- In-place updates ---
        for col in ['FinishWt', 'StructureWt', 'FoundationWt']:
            if col not in gdf.columns:
                gdf[col] = np.nan

        # Iterate through *unique* combinations of Occ and FoundationType.
        for (occupancy, found_type) in gdf[[fields.occupancy_type, 'FoundType']].drop_duplicates().values:
            # Create the lookup key.
            lookup_key = f"{occupancy}_{found_type}"

            # Check if the key exists in the lookup table.
            if lookup_key in lookup_df.index:
                # Get the IntervalIndex for this key.
                interval_index = pd.IntervalIndex(lookup_df.loc[lookup_key, 'IntervalIndex'])

                # Find buildings matching the current occupancy and foundation type.
                mask = (gdf[fields.occupancy_type] == occupancy) & (gdf['FoundType'] == found_type)

                # Use the IntervalIndex to find matching depths *very efficiently*.
                # This is the core of the interval-based lookup.
                depths = gdf.loc[mask, fields.depth_in_structure]
                
                # Initialize arrays to collect results; using np.where is much faster
                indices = []
                FinishWts = []
                StructureWts = []
                FoundationWts = []          

                #Use get_indexer to return array positions of matching intervals.
                matching_intervals_positions = interval_index.get_indexer(depths)

                #get the interval objects themselves via array positioning
                matching_intervals = interval_index[matching_intervals_positions]

                #Extract relevant lookup info from the lookuptable for those intervals (avoid iterrows)
                for interval in matching_intervals:                
                    if pd.notna(interval):#make sure there is a match, -1 from get_indexer if none
                        indices.append(interval.left) #left side is an easy key
                        lookup_row = lookup_df.loc[lookup_key].loc[str(interval.left)] #single row returned if unique, otherwise first row chosen
                        FinishWts.append(lookup_row['FinishWt'])
                        StructureWts.append(lookup_row['StructureWt'])
                        FoundationWts.append(lookup_row['FoundationWt']) 
                    else: #Handle the no-match condition and add the appropriate nan value.
                        indices.append(np.nan)
                        FinishWts.append(np.nan)
                        StructureWts.append(np.nan)
                        FoundationWts.append(np.nan)
                
                #Apply the values to building dataframe, use of np.where keeps alignment with depth index.
                gdf.loc[mask, 'FinishWt'] = np.where(pd.notna(indices), FinishWts, np.nan)          
                gdf.loc[mask, 'StructureWt'] = np.where(pd.notna(indices), StructureWts, np.nan)  
                gdf.loc[mask, 'FoundationWt'] = np.where(pd.notna(indices), FoundationWts, np.nan)


        gdf.drop(columns=['FoundType'], inplace=True)

        


    def _calculate_debris_inplace(self, debris_df: pd.DataFrame):
        """
        Calculates debris weights and amounts in a vectorized manner,
        modifying the input GeoDataFrame in place.

        Args:
            gdf: GeoDataFrame with building data.  Must contain columns:
                'flood_depth', 'occupancy_type', 'foundation_type', 'area'
                Modified in place to add debris calculation results.
            debris_df: DataFrame with debris weight lookup data. Must contain columns:
                'SOccup', 'FoundType', 'MinFloodDepth', 'MaxFloodDepth',
                'FinishWt', 'StructureWt', 'FoundationWt'
            fields: An object with string attributes for column names (as before).
        """

        # --- 1. Prepare the Lookup Table (debris_df) ---
        gdf = self.buildings.gdf
        fields = self.buildings.fields

        # Create a 'FoundType' column in gdf to match debris_df
        gdf['FoundType'] = np.where(gdf[fields.foundation_type].isin(["S", "F"]), "Slab", "Footing")

        # Ensure correct data types
        debris_df['MinFloodDepth'] = debris_df['MinFloodDepth'].astype(float)
        debris_df['MaxFloodDepth'] = debris_df['MaxFloodDepth'].astype(float)
        gdf[fields.flood_depth] = gdf[fields.flood_depth].astype(float)


        # --- 2. Vectorized Lookup using Merge ---

        # Merge based on occupancy and foundation type first.  Use a temporary DataFrame
        temp_df = pd.merge(
            gdf,
            debris_df,
            left_on=[fields.occupancy_type, "FoundType"],
            right_on=["SOccup", "FoundType"],
            how="left",
        )

        # --- 3. Vectorized Filtering based on Flood Depth ---

        # Create a boolean mask for flood depth
        depth_mask = (temp_df[fields.flood_depth] >= temp_df["MinFloodDepth"]) & (
            temp_df[fields.flood_depth] < temp_df["MaxFloodDepth"]
        )

        # Apply the mask, setting weights to 0 where the condition is false.
        temp_df.loc[~depth_mask, ["FinishWt", "StructureWt", "FoundationWt"]] = 0

        # --- 4. Calculate Debris (In-Place on gdf) ---

        # Now perform calculations directly, using the temporary DataFrame's columns.
        gdf[fields.debris_finish] = gdf[fields.area] * temp_df["FinishWt"] / 1000
        gdf[fields.debris_foundation] = gdf[fields.area] * temp_df["FoundationWt"] / 1000
        gdf[fields.debris_structure] = gdf[fields.area] * temp_df["StructureWt"] / 1000
        gdf[fields.debris_total] = (
            gdf[fields.debris_finish]
            + gdf[fields.debris_foundation]
            + gdf[fields.debris_structure]
        )

        # --- 5. Clean Up (In-Place) ---
        # Remove the temporary 'FoundType' column from gdf.
        gdf.drop(columns=['FoundType'], inplace=True)



    def lookup_debris_weights(self, flood_depth, occupancy, foundation_type):
        """
        Given a flood depth, occupancy, and foundation type, return the weight values
        from debris_df based on matching rules.

        Args:
            flood_depth (float): The flood depth of the building.
            occupancy (str): The occupancy type of the building.
            foundation_type (str): The foundation type (e.g., "S", "F", etc.)

        Returns:
            pd.Series: A series with keys ['FinishWt', 'StructureWt', 'FoundationWt'].
        """
        debris_df = self.debris

        # Determine the found type based on foundation type:
        # For Slab matching, foundation types S or F; all others as Footing.
        found_type = "Slab" if foundation_type in ["S", "F"] else "Footing"
        df = debris_df[
            (debris_df["SOccup"] == occupancy) & (debris_df["FoundType"] == found_type)
        ]

        # Find the matching row(s)
        match = df[
            (flood_depth >= df["MinFloodDepth"]) & (flood_depth < df["MaxFloodDepth"])
        ]
        if not match.empty:
            # If multiple rows match (for different types like 'Footing' and 'Slab'),
            # you could either choose one or combine them as needed.
            # For this example, we'll take the first match.
            row = match.iloc[0]
            return pd.Series(
                {
                    "FinishWt": row["FinishWt"],
                    "StructureWt": row["StructureWt"],
                    "FoundationWt": row["FoundationWt"],
                }
            )
        # Return defaults if no match is found
        return pd.Series({"FinishWt": 0, "StructureWt": 0, "FoundationWt": 0})

    def lookup_restoration_time(self, flood_depth, occupancy):
        """
        Given a flood depth, occupancy, and return the weight values
        from restoration_df based on matching rules.

        Args:
            flood_depth (float): The flood depth of the building.
            occupancy (str): The occupancy type of the building.

        Returns:
            pd.Series: A series with keys ['Min_Restor_Days', 'Max_Restor_Days'].
        """
        restoration_df = self.restoration

        df = restoration_df[(restoration_df["SOccup"] == occupancy)]

        # Find the matching row(s)
        match = df[(flood_depth >= df["Min_Depth"]) & (flood_depth < df["Max_Depth"])]
        if not match.empty:
            # If multiple rows match (for different types like 'Footing' and 'Slab'),
            # you could either choose one or combine them as needed.
            # For this example, we'll take the first match.
            row = match.iloc[0]
            return pd.Series(
                {
                    "Min_Restor_Days": row["Min_Restor_Days"],
                    "Max_Restor_Days": row["Max_Restor_Days"],
                }
            )
        # Return defaults if no match is found
        return pd.Series(
            {
                "Min_Restor_Days": 0,
                "Max_Restor_Days": 0,
            }
        )
