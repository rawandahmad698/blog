import yaml
import os


def parse_paragraphs(yml_file_name: str) -> dict:
    post_data = {}
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    yml_file_path = os.path.join(parent_dir, 'static', 'posts', yml_file_name)

    try:
        with open(yml_file_path) as f:
            paragraphs_list = []
            links_list = []

            post_data_raw = yaml.safe_load(f)
            post_title = post_data_raw['title']
            post_description = post_data_raw['description']
            post_image = post_data_raw['image']
            post_data['title'] = post_title
            post_data['description'] = post_description
            post_data['image'] = post_image
            post_data['timestamp'] = post_data_raw['timestamp']

            paragraphs = post_data_raw['paragraphs']
            paragraph_dict = {}

            for paragraph in paragraphs:
                paragraph_dict['text'] = paragraph['text']
                paragraph_dict['type'] = paragraph['type']
                if paragraph['type'] == 'image':
                    paragraph_dict['image'] = paragraph['image']

                paragraphs_list.append(paragraph_dict)

            links = post_data_raw['links']
            for link in links:
                link_dict = {'title': link['title'], 'url': link['url']}
                links_list.append(link_dict)

            post_data['paragraphs'] = paragraphs
            post_data['links'] = links_list

            f.close()
    except FileNotFoundError:
        print(">> Could not find file: {}".format(yml_file_path))
    except Exception as e:
        print(">> Error while parsing file: {}".format(e))

    return post_data
