import oci
import csv

config = oci.config.from_file()
search_client = oci.resource_search.ResourceSearchClient(config)

# 텍스트 파일 읽어서 각 라인을 배열로 저장
with open('ocids.txt', 'r') as file:
    ocids = [line.strip() for line in file]  # 각 라인의 공백 및 줄바꿈 제거

# 20개씩 그룹으로 나누기
def chunk_ocids(ocids, chunk_size):
    return [ocids[i:i + chunk_size] for i in range(0, len(ocids), chunk_size)]

# OCID 그룹화
ocid_groups = chunk_ocids(ocids, 20)

def search_resources(ocid_group):
    structured_search_details = oci.resource_search.models.StructuredSearchDetails(
        query=f"query all resources where identifier in ({', '.join(f'\'{ocid}\'' for ocid in ocid_group)})",
        matching_context_type="NONE"
    )
    return search_client.search_resources(structured_search_details)

# 데이터를 CSV로 저장할 함수
def save_to_csv(data):
    with open('resources.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)

try:
    # 빈 리스트를 생성하여 데이터를 담기 위한 준비
    result_list = []
    global_index = 1

    for group_index, group in enumerate(ocid_groups):
        # Process each group
        response = search_resources(group)
        
        for resource in response.data.items:
            # Use the global_index to print the global order
            # print(f"{global_index}, {resource.identifier}, {resource.display_name}")
            result_list.append([global_index, resource.identifier, resource.display_name])
            global_index += 1  # Increment the global index after each print

    save_to_csv(result_list)
    print("데이터가 CSV 파일에 저장되었습니다.")

except oci.exceptions.ServiceError as e:
    print(f"Service error: {e.message}")
except Exception as e:
    print(f"An error occurred: {e}")

