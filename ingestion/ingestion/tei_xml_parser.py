"""
This module contains the TeiXmlParser class to Extract, Load and Transform data
    from xml corpora in the TEI format into SQL databases using sqlalchemy.
"""
import uuid
from typing import List

from lxml import etree

from .database_connector import DatabaseConnector
from . import tei_sql_schema as schema


class TeiXmlParser(DatabaseConnector):
    """
    Class extracting information from a xml corpus and transforming it to sqlalchemy
        objects.
        This class inherits from DatabaseConnector allowing it to directly push
        parsed copora into the connected database.
    """

    def __init__(self, user: str, password: str, host: str, port: str, database: str):
        """
        Args:
            user: username to connect to the database service
            password: ...
            host: host url
            port: service port
            database: name of the target database
        """
        super().__init__(user, password, host, port, database)
        self.tree = None
        self.root = None
        self.xmlns_header = None

    def __call__(self, xml_string: str) -> None:
        """
        Sugar to allow directly calling the parser object.
        Just calls self.parse_and_push

        Args:
            xml_string: string containing xml corpus
        """
        self.parse_and_push(xml_string)

    def parse_and_push(self, xml_string: str) -> None:
        """
        Extract the content from the xml corpus, transform it to sqlalchemy objects and
            load it into the connected database.

        Args:
            xml_string: string containing xml corpus
        """
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
        """
        Wrap the tag with the main namespace.

        Args:
            tag: string to wrap with namespace.

        Returns:
            String of wrapped tag.
        """
        return f"\u007b{self.xmlns_header}\u007d{tag}"

    # cast information
    def parse_cast_list(self, tree: etree._ElementTree) -> List[schema.Base]:
        """
        Get CastList object and extract all necessary information.

        Args:
            tree: xml tree object to search for CastList object.

        Returns:
            List of db objects found and transformed from the CastList object.
        """
        elements = []
        for cast_group in tree.findall(f".//{self.xmlns('castList')}"):
            elements.extend(self.parse_cast_group(cast_group))
        return elements

    def parse_cast_group(self, cast_group: etree._Element) -> List[schema.Base]:
        """
        Extract information from CastGroup object.

        Args:
            cast_group: xml subtree to parse

        Returns:
            List of db objects found and transformed from the CastGroup object.
        """
        db_cast_group = schema.CastGroup()
        elements = [db_cast_group]

        for cast_item in cast_group.findall(f".//{self.xmlns('castItem')}"):
            elements.extend(self.parse_cast_item(
                cast_item, cast_group_id=db_cast_group.id))
        return elements

    def get_cast_item_id(self, cast_item: etree._Element) -> str:
        """
        Get the id of the provided CastItem object,
            or generate a uuid4 if no id can be found.

        Args:
            cast_item: CastItem xml subtree

        Returns:
            string of id
        """
        # TODO: find a better solution, maybe expand default xml namespace?
        id_keys = [key for key in cast_item.attrib.keys() if key.endswith("}id")]
        id_key = "[None]"
        if id_keys:
            id_key = id_keys[0]

        # TODO: pretty ugly to it like this -> find better solution!
        cast_item_id = cast_item.attrib.get("sameAs") \
                       or cast_item.attrib.get(id_key) \
                       or str(uuid.uuid4())
        return cast_item_id

    def parse_cast_item(
            self, cast_item: etree._Element, cast_group_id: int) -> List[schema.Base]:
        """
        Extract information from CastItem object.

        Args:
            cast_item: CastItem xml subtree
            cast_group_id: int id of the respective CastGroup object the CastItem
                belongs to

        Returns:
            List of db objects found and transformed from the CastItem object.
        """

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

    def parse_cast_role(
            self, cast_item: etree._Element, cast_item_id: str) -> schema.CastRole:
        """
        Extract information from CastRole object.

        Args:
            cast_item: CastItem xml subtree the Role and RoleDescription objects are
                contained id.
            cast_item_id: string id of the respective CastItem object.

        Returns:
            List of db objects found and transformed from the CastItem object.
        """
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
