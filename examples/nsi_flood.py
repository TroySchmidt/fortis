import os
import time
from fortis.engine.analyses.hazus_flood import HazusFloodAnalysis
from fortis.engine.models.flood_depth_grid import FloodDepthGrid
from fortis.engine.vulnerability.default_flood import DefaultFloodFunction
from fortis.engine.models.nsi_buildings import NsiBuildings

def run_nsi_flood():
    overall_start_time = time.time()  
    # Define file paths (adjust these paths as necessary)
    base_dir = os.path.dirname(__file__)
    buildings_gpkg = os.path.join(base_dir, "nsi_2022_15.gpkg")
    tif_file = os.path.join(base_dir, "Oahu_10_withReef.tif")

    # Load NSI buildings data from GPKG
    step_start = time.time()
    buildings = NsiBuildings(buildings_gpkg, "nsi")
    print(f"Loading buildings data took: {time.time() - step_start:.6f} seconds")

    # Read the depth grid from the TIFF file
    step_start = time.time()
    depth_grid = FloodDepthGrid(tif_file)
    print(f"Loading depth grid took: {time.time() - step_start:.6f} seconds")

    # Create an instance of the default flood function
    step_start = time.time()
    flood_function = DefaultFloodFunction(buildings, flood_type="R")
    print(f"Creating vulnerability function took: {time.time() - step_start:.6f} seconds")

    # Create the Hazus flood analyzer instance
    step_start = time.time()
    analyzer = HazusFloodAnalysis(
        buildings=buildings,
        vulnerability_func=flood_function,
        depth_grid=depth_grid,
    )
    print(f"Creating analyzer took: {time.time() - step_start:.6f} seconds")

    # Calculate losses using the analysis
    step_start = time.time()
    analyzer.calculate_losses()
    print(f"Calculating losses took: {time.time() - step_start:.6f} seconds")

    # Save the results to multiple formats
    results_base = os.path.join(base_dir, "nsi_flood_losses")
    
    # 1. Save as CSV
    step_start = time.time()
    csv_path = f"{results_base}.csv"
    buildings.gdf.to_csv(csv_path, index=False)
    print(f"Saving to CSV took: {time.time() - step_start:.6f} seconds")
    
    # 2. Save as GeoPackage
    step_start = time.time()
    gpkg_path = f"{results_base}.gpkg"
    buildings.gdf.to_file(gpkg_path, driver="GPKG")
    print(f"Saving to GeoPackage took: {time.time() - step_start:.6f} seconds")
    
    overall_end_time = time.time()
    elapsed_time = overall_end_time - overall_start_time
    
    print(f"Total execution time: {elapsed_time:.6f} seconds")
    print(f"NSI Flood analysis of {len(buildings.gdf):,} buildings complete.")
    print(f"Results saved to:")
    print(f"  - CSV: {csv_path}")
    print(f"  - GeoPackage: {gpkg_path}")


if __name__ == "__main__":
    run_nsi_flood()
