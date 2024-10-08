import json
from md_utils import MarkdownGenerator

# Load the JSON file
with open('doc-rdl.json', 'r') as json_file:
    data = json.load(json_file)

# Initialize the Markdown generator
md = MarkdownGenerator()

# Extract the dataset information (assuming the first dataset in the list)
dataset = data.get('datasets', [])[0]  # Taking the first dataset as an example
dataset_id = dataset.get('id', 'N/A')
dataset_title = dataset.get('title', 'N/A')
dataset_description = dataset.get('description', 'N/A')
dataset_project = dataset.get('project', 'N/A')
dataset_details = dataset.get('details', 'N/A')
dataset_license = dataset.get('license', 'N/A')
contact_point = dataset.get('contact_point', {})
contact_name = contact_point.get('name', 'N/A')
contact_email = contact_point.get('email', 'N/A')

# Add sections using the Markdown generator
md.add_header("Model Information")
md.add_definition("Name", dataset_project)
md.add_definition("Description", dataset_details)
md.add_definition("License", dataset_license)
md.add_definition("Contact", f"{contact_name} {contact_email}")

# Hazard module heading
md.add_header("Hazard module", level=2)
md.add_definition("ID", dataset_id)
md.add_definition("Title", dataset_title)
md.add_definition("Description", dataset_description)

# Event set information table
md.add_header("Event set information", level=3)
headers = ["Event Set", "Type", "Calculation Method", "Countries", "Number of events"]
rows = []

# Loop through event_sets and add rows to the Markdown table
event_sets = dataset.get('hazard', {}).get('event_sets', [])
for event_set in event_sets:
    event_set_name = event_set.get('id', 'N/A')
    analysis_type = event_set.get('analysis_type', 'N/A')
    calculation_method = event_set.get('calculation_method', 'N/A')
    spatial = event_set.get('spatial', {})
    countries = spatial.get('countries', 'N/A')
    event_count = event_set.get('event_count', 'N/A')
    row = [event_set_name, analysis_type, calculation_method, countries, event_count]
    rows.append([str(r) for r in row])

md.add_table(headers, rows)

# Hazard information table
md.add_header("Hazard information", level=3)
headers = ["Event Set", "Process types", "Intensity measure", "Trigger type", "Trigger process types"]
rows = []

# Loop through event_sets and hazards and add rows to the Markdown table
for event_set in event_sets:
    hazards = event_set.get('hazards', [])
    for hazards_obj in hazards:
        hazards_type = hazards_obj.get('id', 'N/A')
        hazards_processes = hazards_obj.get('processes', 'N/A')
        intensity_measure = hazards_obj.get('intensity_measure', 'N/A')
        trigger = hazards_obj.get('trigger', {})
        trigger_type = trigger.get('type', 'N/A')
        trigger_processes = trigger.get('processes', 'N/A')

        row = [hazards_type, hazards_processes, intensity_measure, trigger_type, trigger_processes]
        rows.append([str(r) for r in row])

md.add_table(headers, rows)

# Vulnerability module heading
md.add_header("Vulnerability module", level=2)

datasetv = data.get('datasets', [])[2]  # Vulnerability

# Get the root attributes
dataset_id = datasetv.get('id', 'N/A')
dataset_title = datasetv.get('title', 'N/A')
dataset_description = datasetv.get('description', 'N/A')
# Extract the vulnerability object from within the dataset
vulnerability = datasetv.get('vulnerability', {})
# Vuln attributes
hazard_primary = vulnerability.get('hazard_primary', 'N/A')
hazard_process_primary = vulnerability.get('hazard_process_primary', 'N/A') 
intensity = vulnerability.get('intensity', 'N/A') 
category = vulnerability.get('category', 'N/A') 
analysis_details = vulnerability.get('analysis_details', 'N/A')

impact = vulnerability.get('impact', {})
impact_type = impact.get('type', 'N/A')
impact_metric = impact.get('metric', 'N/A')
impact_unit = impact.get('unit', 'N/A')
impact_base_data_type = impact.get('base_data_type', 'N/A')

spatial = vulnerability.get('spatial', {})
countries = spatial.get('countries', 'N/A')

functions = vulnerability.get('functions', {})
vuln_function = functions.get('vulnerability', {})
approach = vuln_function.get('approach', 'N/A')

md.add_definition("ID", dataset_id)
md.add_definition("Title", dataset_title)
md.add_definition("Description", dataset_description)

md.add_header("Hazard information", level=3)
md.add_table(["Hazard type", "Hazard process", "Intensity"],
                          [[hazard_primary, hazard_process_primary, intensity]])

md.add_header("Vulnerability functions", level=3)
md.add_definition("Exposure category", category)
md.add_definition("Countries", countries)
md.add_definition("Impact type", impact_type)
md.add_definition("Impact metric", impact_metric)
md.add_definition("Impact unit", impact_unit)
md.add_definition("Base data type", impact_base_data_type)
md.add_definition("Approach", approach)

md.add_header("Further details", level=3)
md.sections.append(f"{analysis_details}\n\n")

# Add footer
md.add_text("This document has been generated using Risk Data Library Standard schema version 0.2.")
md.add_text("For more information about the RDLS please visit [RDLS](https://docs.riskdatalibrary.org/en/latest/)")

# Get the final markdown content
markdown_content = md.get_markdown()

# Write the output to a markdown file
with open('../doc.md', 'w') as md_file:
    md_file.write(markdown_content)

print("Markdown file generated successfully!")
