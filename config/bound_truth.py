"""
Ground truth
Copyright 2017 @ Georgetown University
"""
import xml.etree.ElementTree as ET
from collections import defaultdict
import math


class Truth:
    """
    truth=
    {
        topic_id:
        {
            subtopic_id:
            {
                doc_no:
                {
                    passage_id:
                    {
                        nugget_id:
                        rating:
                    }
                }
            }
        }
    }
    """

    def __init__(self, truth_xml_path, doc_length):
        self.truth = defaultdict(dict)

        self.doc_length = {}
        if doc_length is not None:
            self.doc_length = doc_length

        root = ET.parse(truth_xml_path).getroot()

        for domain in list(root):
            for topic in list(domain):
                topic_id = topic.attrib['id']

                for subtopic in list(topic):
                    if subtopic.tag == 'subtopic':
                        subtopic_id = subtopic.attrib['id']
                        subtopic_data = defaultdict(dict)
                        nugget_id = ''
                        doc_no, rating = '', 0
                        for passage in list(subtopic):
                            passage_data = {}
                            passage_id = passage.attrib['id']

                            for tag_under_passage in list(passage):
                                if tag_under_passage.tag == 'docno':
                                    doc_no = tag_under_passage.text
                                elif tag_under_passage.tag == 'rating':
                                    rating = int(tag_under_passage.text)
                                    if rating == 0:
                                        rating = 1
                                elif tag_under_passage.tag == 'type':
                                    if tag_under_passage.text == 'MANUAL':
                                        nugget_id = passage_id

                            passage_data['nugget_id'] = nugget_id
                            passage_data['rating'] = rating

                            subtopic_data[doc_no][passage_id] = passage_data

                        self.truth[topic_id][subtopic_id] = subtopic_data

    def truth4CT(self, topic_id):
        """return doc_no: {subtopic_id: rating}, subtopic_num"""

        return_data = defaultdict(dict)
        for subtopic_id, subtopic_data in self.truth[topic_id].items():
            for doc_no, doc_data in subtopic_data.items():
                ratings = []
                for _, passage_data in doc_data.items():
                    ratings.append(passage_data['rating'])
                ratings = sorted(ratings, reverse=True)
                # print(ratings)
                r1 = 0  # with discount
                r2 = 0  # no discount
                for i in range(len(ratings)):
                    r1 += ratings[i] / math.log(i + 2, 2)
                    r2 += ratings[i]
                return_data[doc_no][subtopic_id] = r2

        return return_data, len(self.truth[topic_id])

    def truth4SDCG(self, topic_id):
        """return doc_no: rating"""
        return_data = defaultdict(int)
        for subtopic_id, subtopic_data in self.truth[topic_id].items():
            for doc_no, doc_data in subtopic_data.items():
                for _, passage_data in doc_data.items():
                    return_data[doc_no] += passage_data['rating']
        return return_data

    def truth4EU_bound(self, topic_id):
        """return nugget_id:[doc_no1, doc_no2, ... ], nugget_id: rating, doc: length"""
        nugget_doc = defaultdict(list)  # nugget -> doc_no list
        nugget_rating = defaultdict(int)  # nugget_id -> rating
        for subtopic_id, subtopic_data in self.truth[topic_id].items():
            for doc_no, doc_data in subtopic_data.items():
                for passage_id, passage_data in doc_data.items():
                    nugget_id = passage_data["nugget_id"]
                    if doc_no not in nugget_doc[nugget_id]:
                        nugget_doc[nugget_id].append(doc_no)

                    nugget_rating[nugget_id] = passage_data['rating']

        return nugget_doc, nugget_rating, self.doc_length

    def truth4recall(self, topic_id):
        """return subtopic_set, doc_set, nugget_set, doc_subtopic, doc_nugget"""
        subtopics = set()
        docs = set()
        nuggets = set()
        doc_nugget = defaultdict(list)  # doc_no -> nugget list
        doc_subtopic = defaultdict(set)  # doc_no -> subtopic set

        for subtopic_id, subtopic_data in self.truth[topic_id].items():
            subtopics.add(subtopic_id)
            for doc_no, doc_data in subtopic_data.items():
                docs.add(doc_no)
                doc_subtopic[doc_no].add(subtopic_id)
                for passage_id, passage_data in doc_data.items():
                    nuggets.add(passage_data['nugget_id'])
                    doc_nugget[doc_no].append(passage_data['nugget_id'])

        return subtopics, docs, nuggets, doc_subtopic, doc_nugget

    def stats(self):
        """print the statistic information about the ground truth"""
        topic_num = 0

        subtopic_num = 0

        total_doc = set()
        doc_num = 0
        for topic_id in self.truth:
            topic_num += 1
            topic_doc = set()
            for subtopic_id in self.truth[topic_id]:
                subtopic_num += 1
                for doc_no in self.truth[topic_id][subtopic_id]:
                    topic_doc.add(doc_no)
                    total_doc.add(doc_no)
            doc_num += len(topic_doc)

        print("Topic num:", topic_num)
        print("Subtopic num:", subtopic_num)
        print("Avg subtopic per topic:", subtopic_num / topic_num)

        print("Total Relevant Documents:", len(total_doc))
        print("Avg doc per topic:", doc_num / topic_num)


if __name__ == '__main__':
    # dd_truth = DDTruth('data/trec_dd_15/truth/dynamic-domain-2015-truth-data-v5.xml')
    dd_truth = Truth('data/trec_dd_16/truth/dynamic-domain-2016-truth-data.xml')
    dd_truth.stats()
    # dd_truth.truth_check_4_EU()
    # dd_truth.self_check()
    import pprint

    # pprint.pprint(dd_truth.truth_4_CT('DD16-1'))
    """
    for  i in range(1, 54):
        topic_id = "DD16-"+str(i)
        t, _ = dd_truth.truth_4_CT(topic_id)
        print(len(t))
    """