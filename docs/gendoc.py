import json

# Load the JSON file
with open('doc-rdl.json', 'r') as json_file:
    data = json.load(json_file)

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

# Extract the hazard object from within the first dataset
hazard = dataset.get('hazard', {})
event_sets = hazard.get('event_sets', [])

# Create the Markdown content
markdown = f"# Model Information\n\n"

markdown += f"**Name**: {dataset_project}\n\n"
markdown += f"**Description**: {dataset_details}\n\n"
markdown += f"**License**: {dataset_license}\n\n"
markdown += f"**Contact**: {contact_name} {contact_email}  \n\n"

# Create a hazard module heading
markdown+= "## Hazard module \n\n"

markdown += f"**ID**: {dataset_id}\n\n"
markdown += f"**Title**: {dataset_title}\n\n"
markdown += f"**Description**: {dataset_description}\n\n"


# Create a Markdown table
markdown += "### Event set information \n\n"
markdown += "| Event Set | Type        | Calculation Method | Countries  | Number of events |\n"
markdown += "|-----------|-------------|--------------------|------------|------------------|\n"

# Loop through event_sets and add rows to the Markdown table
for event_set in event_sets:
    event_set_name = event_set.get('id', 'N/A')
    analysis_type = event_set.get('analysis_type', 'N/A')
    calculation_method = event_set.get('calculation_method', 'N/A')
    spatial = event_set.get('spatial', 'N/A')
    countries = spatial.get('countries','N/A')
    event_count = event_set.get('event_count', 'N/A')
    
    markdown += f"| {event_set_name} | {analysis_type} | {calculation_method} | {countries} | {event_count} |\n"

markdown += "\n"
markdown += "### Hazard information \n\n"
markdown += "| Event Set | Process types | Intensity measure | Trigger type  | Trigger process types |\n"
markdown += "|-----------|---------------|-------------------|---------------|-----------------------|\n"

# Loop through event_sets and hazards and add rows to the Markdown table
for event_set in event_sets:
    hazards = event_set.get('hazards', [])
    for hazards_obj in hazards:
        hazards_type = hazards_obj.get('id','N/A')
        hazards_processes = hazards_obj.get('processes','N/A')
        intensity_measure = hazards_obj.get('intensity_measure','N/A')
        trigger = hazards_obj.get('trigger','N/A')
        trigger_type = trigger.get('type','N/A')
        trigger_processes = trigger.get('processes','N/A')

        markdown += f"| {hazards_type} | {hazards_processes} | {intensity_measure} | {trigger_type} | {trigger_processes} |\n"


# Create a vulnerability module heading
markdown+= "\n## Vulnerability module \n\n"

datasetv = data.get('datasets', [])[2]  # Vulnerability

# Get the root attributes
dataset_id = datasetv.get('id', 'N/A')
dataset_title = datasetv.get('title', 'N/A')
dataset_description = datasetv.get('description', 'N/A')
# Extract the vuln object from within the dataset
vulnerability = datasetv.get('vulnerability', {})
# Vuln attributes
hazard_primary = vulnerability.get('hazard_primary','N/A')
hazard_process_primary = vulnerability.get('hazard_process_primary','N/A') 
intensity = vulnerability.get('intensity','N/A') 
category = vulnerability.get('category','N/A') 
analysis_details = vulnerability.get('analysis_details','N/A')

impact = vulnerability.get('impact',{})
impact_type = impact.get('type','N/A')
impact_metric = impact.get('metric','N/A')
impact_unit = impact.get('unit','N/A')
impact_base_data_type = impact.get('base_data_type','N/A')

spatial = vulnerability.get('spatial',{})
countries = spatial.get('countries','N/A')

functions = vulnerability.get('functions',{})
vuln_function = functions.get('vulnerability',{})
approach = vuln_function.get('approach','N/A')

markdown += f"**ID**: {dataset_id}\n\n"
markdown += f"**Title**: {dataset_title}\n\n"
markdown += f"**Description**: {dataset_description}\n\n"

markdown += "### Hazard information \n\n"
markdown += "| Hazard type | Hazard process | Intensity |\n"
markdown += f"| {hazard_primary} | {hazard_process_primary} | {intensity} |\n"

markdown += "\n### Vulnerability functions \n\n"

markdown += f"**Exposure category**: {category}\n\n"
markdown += f"**Countries**: {countries}\n\n"
markdown += f"**Impact type**: {impact_type}\n\n"
markdown += f"**Impact metric**: {impact_metric}\n\n"
markdown += f"**Impact unit**: {impact_unit}\n\n"
markdown += f"**Base data type**: {impact_base_data_type}\n\n"
markdown += f"**Approach**: {approach}\n\n"

markdown += "### Further details \n\n"
markdown += f"{analysis_details}\n\n"

markdown += "\nThis document has been generated using Risk Data Library Standard schema version 0.2. For more information about the RDLS please visit [RDLS](https://docs.riskdatalibrary.org/en/latest/)"

# Write the output to a markdown file
with open('../doc.md', 'w') as md_file:
    md_file.write(markdown)

print("Markdown file generated successfully!")
