import uuid
from typing import List

from lxml import etree

from .database_connector import DatabaseConnector
from . import tei_sql_schema as schema


class TeiXmlParser(DatabaseConnector):

    def __init__(self, user: str, password: str, host: str, port: str, database: str):
        super().__init__(user, password, host, port, database)
        self.tree = None
        self.root = None
        self.xmlns_header = None

    def __call__(self, xml_string: str):
        self.parse_and_push(xml_string)

    def parse_and_push(self, xml_string: str):
        self.tree = etree.fromstring(xml_string)
        self.root = None
        if isinstance(self.tree, etree._Element):
            self.root = self.tree
        else:
            self.root = self.tree.getroot()
        self.xmlns_header = list(self.root.nsmap.values())[0]

        elements = []
        # parse meta information
        # TODO: parse meta information

        # parse cast information
        elements.extend(self.parse_cast_list(self.tree))

        # parse play information
        # TODO: parse play information

        self.bulk_insert(elements)

    # meta information
    def xmlns(self, tag: str) -> str:
        return f"\u007b{self.xmlns_header}\u007d{tag}"

    # cast information
    def parse_cast_list(self, tree: etree._ElementTree) -> List[schema.Base]:
        elements = []
        for cast_group in tree.findall(f".//{self.xmlns('castList')}"):
            elements.extend(self.parse_cast_group(cast_group))
        return elements

    def parse_cast_group(self, cast_group: etree._Element) -> List[schema.Base]:
        db_cast_group = schema.CastGroup()
        elements = [db_cast_group]

        for cast_item in cast_group.findall(f".//{self.xmlns('castItem')}"):
            elements.extend(self.parse_cast_item(
                cast_item, cast_group_id=db_cast_group.id))
        return elements

    def get_cast_item_id(self, cast_item: etree._Element) -> str:
        # TODO: find a better solution, maybe expand default xml namespace?
        id_keys = [key for key in cast_item.attrib.keys() if key.endswith("}id")]
        id_key = "[None]"
        if id_keys:
            id_key = id_keys[0]

        cast_item_id = cast_item.attrib.get("sameAs") \
                       or cast_item.attrib.get(id_key) \
                       or str(uuid.uuid4())
        if not cast_item_id:
            print("ALARM:", cast_item, cast_item.attrib, cast_item.text)
        return cast_item_id

    def parse_cast_item(
            self, cast_item: etree._Element, cast_group_id: int) -> List[schema.Base]:

        name_obj = cast_item.find(f"{self.xmlns('role')}/{self.xmlns('name')}")

        db_cast_item = schema.CastItem(
            id=self.get_cast_item_id(cast_item),
            cast_group_id=cast_group_id,
            content=" ".join([el.strip() for el in cast_item.itertext() if el.strip()]),
            name=name_obj.text if name_obj else ""
        )
        elements = [
            db_cast_item,
            self.parse_cast_role(
                cast_item=cast_item, cast_item_id=db_cast_item.id)]
        return elements

    def parse_cast_role(self, cast_item: etree._Element,
                        cast_item_id: str) -> schema.CastRole:
        content = " ".join([el.strip() for el in cast_item.itertext() if el.strip()])
        name_obj = cast_item.find(f"{self.xmlns('role')}/{self.xmlns('name')}")
        desc_obj = cast_item.find(f"{self.xmlns('roleDesc')}")

        return schema.CastRole(
            cast_item_id=cast_item_id or cast_item.attrib.get("sameAs"),
            content=content,
            name=name_obj.text if name_obj else "",
            description=desc_obj.text if desc_obj else ""
        )

    # play information
    # TODO: define functions to parse play information
