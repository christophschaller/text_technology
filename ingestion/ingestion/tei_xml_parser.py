"""
This module contains the TeiXmlParser class to Extract, Load and Transform data
    from xml corpora in the TEI format into SQL databases using sqlalchemy.
"""
import uuid
from typing import Dict, List

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

        self.temp_cast = {}

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
        elements.extend(self.parse_body(self.tree))

        # self.bulk_insert(elements)

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

        # print("\n###PARSE CAST###\n")
        # for el in elements:
        #     print(el.id, type(el))
        #     print()

        return elements

    def parse_cast_group(self, cast_group: etree._Element) -> List[schema.Base]:
        """
        Extract information from CastGroup object.

        Args:
            cast_group: xml subtree to parse

        Returns:
            List of db objects found and transformed from the CastGroup object.
        """
        db_cast_group = schema.CastGroup(
            id=str(uuid.uuid4())
        )
        elements = [db_cast_group]
        self.insert(db_cast_group)

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
            self, cast_item: etree._Element, cast_group_id: str) -> List[schema.Base]:
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
            id=self.get_cast_item_id(cast_item).strip("#"),
            cast_group_id=cast_group_id,
            content=" ".join([el.strip() for el in cast_item.itertext() if el.strip()]),
            name=name_obj.text if name_obj else ""
        )
        self.insert(db_cast_item)
        self.temp_cast[db_cast_item.id] = db_cast_item
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

        db_cast_role = schema.CastRole(
            id=str(uuid.uuid4()),
            cast_item_id=cast_item_id or cast_item.attrib.get("sameAs"),
            content=content,
            name=name_obj.text if name_obj else "",
            description=desc_obj.text if desc_obj else ""
        )
        self.insert(db_cast_role)
        return db_cast_role

    # play information
    def parse_body(self, tree: etree._ElementTree) -> List[schema.Base]:
        """
        Get all act objects from the body and extract all necessary information.

        Args:
            tree: xml tree object to search for the body object.

        Returns:
            List of db objects found and transformed from the body object.
        """
        elements = []
        body = tree.find(f".//{self.xmlns('body')}")
        act_query = self.xmlns("div[@type='act']")
        for act in body.findall(f".//{act_query}"):
            elements.extend(self.parse_act(act))

        # print("\n###PARSER BODY###\n")
        # for el in elements:
        #     print(el.id, type(el))
        #     print()

        return elements

    def parse_act(self, act: etree._Element) -> List[schema.Base]:
        """
        Parse act instance

        Args:
            act: xml subtree

        Returns:
            List of objects, containing this act and all its children.
        """
        act_head = act.find(f".//{self.xmlns('head')}")
        db_act = schema.Act(
            id=str(uuid.uuid4()),
            content=" ".join([el.strip() for el in act_head.itertext() if el.strip()]),
        )
        elements = [db_act]
        self.insert(db_act)

        scene_query = self.xmlns("div[@type='scene']")
        for scene in act.findall(f".//{scene_query}"):
            elements.extend(self.parse_scene(scene, act_id=db_act.id))
        return elements

    def parse_scene(self, scene: etree._Element, act_id: str) -> List[schema.Base]:
        """
        Parse scene instance.

        Args:
            scene: xml subtree.
            act_id: int id of parent act

        Returns:
            List of objects, containing this scene and all its children.
        """
        scene_head = scene.find(f".//{self.xmlns('head')}")
        db_scene = schema.Scene(
            id=str(uuid.uuid4()),
            act_id=act_id,
            content=" ".join([el.strip() for el in scene_head.itertext() if el.strip()])
        )
        elements = [db_scene]
        self.insert(db_scene)

        stage_query = self.xmlns('stage[@who]')
        for stage in scene.findall(f".//{stage_query}"):
            elements.append(self.parse_stage(stage, scene_id=db_scene.id))

        for speech in scene.findall(f".//{self.xmlns('sp')}"):
            elements.extend(self.parse_speech(speech, scene_id=db_scene.id))
        return elements

    def get_id(self, attrib: Dict) -> str:
        """
        Get id object contained in attrib dict.

        Args:
            attrib: dict of attributes.

        Returns:
            value of element with key ending in "id".
        """
        id_key = [key for key in attrib.keys() if key.endswith("}id")][0]
        return attrib[id_key]

    def parse_stage(self, stage: etree._Element, scene_id: str) -> schema.Stage:
        """
        Parse a stage instance.

        Args:
            stage: xml subtree
            scene_id: int id of the parent scene

        Returns:
            Stage object.
        """
        db_stage = schema.Stage(
            id=self.get_id(stage.attrib),
            scene_id=scene_id,
            content=" ".join([el.strip() for el in stage.itertext() if el.strip()]),
            cast=[self.temp_cast[cast.strip("#")]
                  for cast in stage.attrib["who"].split()],
        )
        self.insert(db_stage)
        return db_stage

    def parse_speech(self, speech: etree._Element, scene_id: str) -> List[schema.Base]:
        """
        Parse a speech instance.

        Args:
            speech: xml subtree
            scene_id: int id of the parent scene

        Returns:
            List of objects containing this speech and all its children.
        """
        db_speech = schema.Speech(
            id=self.get_id(speech.attrib),
            scene_id=scene_id,
            cast_item_id=speech.attrib["who"].split()[0].strip("#")
        )
        elements = [db_speech]
        self.insert(db_speech)

        for line in speech.findall(f".//{self.xmlns('l')}"):
            elements.extend(self.parse_line(line, speech_id=db_speech.id))
        return elements

    def parse_line(self, line, speech_id: str) -> List[schema.Base]:
        """
        Parse a line instance.

        Args:
            line: xml subtree
            speech_id: str id name of the parent speech

        Returns:
            List of objects containing this line and its children tokens.
        """
        db_line = schema.Line(
            id=self.get_id(line.attrib),
            speech_id=speech_id
        )
        elements = [db_line]
        self.insert(db_line)

        for token in line.findall(f".//{self.xmlns('w')}"):
            elements.append(self.parse_token(token, line_id=db_line.id))
        return elements

    def parse_token(self, token, line_id: str) -> schema.Token:
        """
        Parse a single token instance, getting most of the information stored
        in the original XML object.

        Args:
            token: xml subtree
            line_id: str id name of the parent line

        Returns:

        """
        db_token = schema.Token(
            id=self.get_id(token.attrib),
            line_id=line_id,
            content=" ".join([el.strip() for el in token.itertext() if el.strip()]),
            lemma=token.attrib["lemma"],
            ana=token.attrib["ana"],
        )
        self.insert(db_token)
        return db_token