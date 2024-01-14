#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
from bs4 import BeautifulSoup
import json

def get_metadata(base_url, repo_url):
    response = requests.get(f"{base_url}/{repo_url}")
    soup = BeautifulSoup(response.content, "html.parser")

    package_name_element = soup.select_one('div.UnitMeta-repo a')
    if package_name_element:
        package_name = package_name_element.text.strip()
    else:
        package_name = "Package name not available."

    version_box = soup.find('div', class_="Versions-list")
    version_links = version_box.find_all("a", class_="js-versionLink")

    metadata_list = []

    for version_link in version_links:
        version_url = f"{base_url}{version_link['href']}"
        version_response = requests.get(version_url)
        version_soup = BeautifulSoup(version_response.content, "html.parser")

        version_number = version_link.text.strip()
        license_element = version_soup.find('span', class_='License')

        if license_element:
            license_info = license_element.text.strip()
        else:
            license_info = "License information not available."

        version_metadata = {
            "version": version_number,
            "license": license_info
        }

        # Fetch additional details for each version
        details_box = version_soup.find('ul', class_="UnitMeta-details").find_all("li")
        go_mod_raw, license_raw, tag_raw, is_stable_raw, more_link_raw = details_box

        go_mod_link = go_mod_raw.find("a")["href"]
        license_dist = True if "check" in license_raw.find("img")["src"] else False
        is_tagged = True if "check" in tag_raw.find("img")["src"] else False
        is_stable = False if "cancel" in is_stable_raw.find("img")["src"] else True

        # Append additional details to the metadata for this version
        version_metadata["details"] = go_mod_link
        version_metadata["redistributable_license"] = license_dist
        version_metadata["tagged_version"] = is_tagged
        version_metadata["stable_version"] = is_stable
        # Add more fields as needed for other details

        metadata_list.append(version_metadata)

    return package_name, metadata_list

base_url = "https://pkg.go.dev"
repo_url = "kraftkit.sh/unikraft/arch?tab=versions"

package_name, metadata_list = get_metadata(base_url, repo_url)

package_url_template = "https://pkg.go.dev/kraftkit.sh@{version}/unikraft/arch"

for metadata in metadata_list:
    version = metadata["version"]
    package_url = package_url_template.format(version=version)
    metadata["package_url"] = package_url

    response = requests.get(package_url)
    if response.status_code == 200:
        html = BeautifulSoup(response.content, "html.parser")
        package_license_element = html.select_one('*[data-test-id="UnitHeader-license"]')

        if package_license_element:
            package_license = package_license_element.text.strip()
            metadata["package_license"] = package_license
        else:
            metadata["package_license"] = "License: N/A"
    else:
        metadata["package_license"] = "Failed to fetch package details."

output = {
    "package_name": package_name,
    "metadata": metadata_list
}

with open("metadata.json", "w") as json_file:
    json.dump(output, json_file, indent=4)

for metadata in metadata_list:
    print(f"Version: {metadata['version']}")
    print(f"Package URL: {metadata['package_url']}")
    print(f"License: {metadata['package_license']}")
    print(f"Details: {metadata['details']}")
    print(f"Redistributable License: {metadata['redistributable_license']}")
    print(f"Tagged Version: {metadata['tagged_version']}")
    print(f"Stable Version: {metadata['stable_version']}")
    print("------------------------")


# In[9]:





# In[28]:


data_list = []
package_url = "https://pkg.go.dev/kraftkit.sh"
response = requests.get(package_url)
text = ""
if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')

    overview_content = soup.find('div', class_='Overview-readmeContent js-readmeContent')
    if overview_content:
            text = overview_content.get_text().strip()
            print(text)
            for metadata in metadata_list:
                metadata['readme'] = text
                data_list.append(metadata)
    else:
            print("Could not find the specified div class.")
else:
        print(f"Failed to fetch URL. Status code: {response.status_code}")


# In[27]:


data_list

