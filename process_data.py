import pandas as pd
import glob
import os

# Path to your data folder
data_folder = "data"

# Step 1: Get all CSV files in the data folder
csv_files = glob.glob(os.path.join(data_folder, "*.csv"))

# Step 2: Read and combine them into one DataFrame
df_list = []
for file in csv_files:
    df = pd.read_csv(file)
    df_list.append(df)

# Combine into one dataframe
data = pd.concat(df_list, ignore_index=True)

# Step 3: Filter only "Pink Morsels"
data = data[data["product"] == "pink morsel"]

# Step 4: Create a new "Sales" column = quantity * price
data["Sales"] = data["quantity"] * data["price"]

# Step 5: Keep only Sales, Date, Region
formatted_data = data[["Sales", "date", "region"]]

# Step 6: Save the cleaned data to a new CSV
output_file = "formatted_output.csv"
formatted_data.to_csv(output_file, index=False)

print(f"Formatted data saved to {output_file}")
