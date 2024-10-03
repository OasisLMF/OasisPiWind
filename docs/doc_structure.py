#### A basic structure for the model information document with labels and RDL paths in comments (path references as found in rdl xls) to scope out where the info will be populated from.
markdown = f"# Model Information\n\n"

markdown+= "\n## Overview \n\n"

### Model Description - datasets[0]/description

markdown+= "\n### Vendor and Model \n\n"

#########Given headers#########
#### Model Developer - datasets[0]/publisher/name
#### Model Name - datasets[0]/project
#### Date first released - missing
#### Date of last update - missing
#### Version - datasets[0]/version

#########Extras#########
#### License - datasets[0]/license
#### Contact name - datasets[0]/contact_point/name
#### Contact email - datasets[0]/contact_point/email
#### Publisher URL - datasets[0]/publisher/url

markdown+= "\n## Perils, sub-perils and other loss causes \n\n"
markdown+= "\n### Perils \n\n"

#### datasets[0]/title
#### datasets[0]/description

##### Table 'Perils'
##### | Event Set | Peril Code | Hazard type | Hazard process | Intensity measure | Trigger type | Trigger process |

markdown+= "\n## Occurrence sets \n\n"


markdown+= "\n## Coverage types and modifiers \n\n"
markdown+= "\n### Coverage types \n\n"
markdown+= "\n### Primary modifiers \n\n"
markdown+= "\n### Secondary modifiers \n\n"
markdown+= "\n## Geographical schemes \n\n"
markdown+= "\n### Broad scope \n\n"
markdown+= "\n### Geographical schemes \n\n"
markdown+= "\n## Other aspects \n\n"
markdown+= "\n### Secondary uncertainty \n\n"
markdown+= "\n### Correlation in secondary uncertainty \n\n"
markdown+= "\n### Ground up loss capping \n\n"
markdown+= "\n## Other information and resources \n\n"

# Write the output to a markdown file
with open('../doc.md', 'w') as md_file:
    md_file.write(markdown)