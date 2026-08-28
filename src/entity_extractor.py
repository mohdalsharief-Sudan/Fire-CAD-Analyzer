
import math
import re
import logging
from typing import Dict, List, Any, Tuple
from shapely.geometry import Point, LineString, Polygon

logger = logging.getLogger(__name__)


class EntityExtractor:
    """Extracts and analyzes fire protection elements from CAD files"""

    def __init__(self, modelspace, doc):
        self.modelspace = modelspace
        self.doc = doc
        self.entities = {
            "sprinklers": [],
            "pipes": [],
            "pumps": [],
            "valves": [],
            "tanks": [],
            "rooms": [],
            "walls": [],
            "texts": [],
            "blocks": [],
            "gas_systems": [],
            "hose_cabinets": [],
            "fire_alarm": []
        }
        self.unit_conversion = self._determine_units()
        logger.info(f"Unit conversion: {self.unit_conversion}")

    def _determine_units(self):
        try:
            extmax = self.doc.header.get("$EXTMAX", (0, 0, 0))
            width = abs(extmax[0])
            if width > 10000:
                return 0.001
            elif width > 1000:
                return 0.01
            elif width > 100:
                return 1.0
            elif width > 10:
                return 0.0254
            else:
                return 1.0
        except:
            return 1.0

    def _to_meters(self, coord):
        try:
            return float(coord) * self.unit_conversion
        except:
            return 0.0

    def extract_all(self):
        for entity in self.modelspace:
            try:
                dxftype = entity.dxftype()
                if dxftype == "INSERT":
                    self._extract_block_entity(entity)
                elif dxftype == "LINE":
                    self._extract_line_entity(entity)
                elif dxftype == "LWPOLYLINE":
                    self._extract_polyline_entity(entity)
                elif dxftype == "CIRCLE":
                    self._extract_circle_entity(entity)
                elif dxftype == "TEXT":
                    self._extract_text_entity(entity)
                elif dxftype == "MTEXT":
                    self._extract_mtext_entity(entity)
            except Exception as e:
                logger.debug(f"Error: {e}")
                continue
        logger.info(f"Extracted: {self._summarize_entities()}")
        return self.entities

    def _extract_block_entity(self, entity):
        try:
            block_name = entity.dxf.name.upper() if hasattr(entity.dxf, "name") else ""
            insert_point = entity.dxf.insert
            layer = entity.dxf.layer.upper() if hasattr(entity.dxf, "layer") else ""
            x = self._to_meters(insert_point[0])
            y = self._to_meters(insert_point[1])
            z = self._to_meters(insert_point[2]) if len(insert_point) > 2 else 0.0
            info = {
                "name": block_name,
                "layer": layer,
                "position": (x, y, z),
                "rotation": getattr(entity.dxf, "rotation", 0),
                "scale": getattr(entity.dxf, "xscale", 1),
                "attributes": self._extract_block_attributes(entity)
            }
            if self._is_sprinkler(block_name, layer):
                info["type"] = "sprinkler"
                info["sprinkler_type"] = self._determine_sprinkler_type(block_name)
                self.entities["sprinklers"].append(info)
            elif self._is_pump(block_name, layer):
                info["type"] = "pump"
                info["pump_type"] = self._determine_pump_type(block_name)
                self.entities["pumps"].append(info)
            elif self._is_gas_system(block_name, layer):
                info["type"] = "gas_system"
                info["gas_type"] = self._determine_gas_type(block_name)
                self.entities["gas_systems"].append(info)
            elif self._is_hose_cabinet(block_name, layer):
                info["type"] = "hose_cabinet"
                self.entities["hose_cabinets"].append(info)
            elif self._is_fire_alarm(block_name, layer):
                info["type"] = "fire_alarm"
                self.entities["fire_alarm"].append(info)
            elif self._is_valve(block_name, layer):
                info["type"] = "valve"
                self.entities["valves"].append(info)
            elif self._is_tank(block_name, layer):
                info["type"] = "tank"
                self.entities["tanks"].append(info)
            else:
                info["type"] = "block"
                self.entities["blocks"].append(info)
        except Exception as e:
            logger.debug(f"Block error: {e}")

    def _extract_line_entity(self, entity):
        try:
            start = entity.dxf.start
            end = entity.dxf.end
            layer = entity.dxf.layer.upper()
            start_m = (self._to_meters(start[0]), self._to_meters(start[1]), self._to_meters(start[2]) if len(start) > 2 else 0.0)
            end_m = (self._to_meters(end[0]), self._to_meters(end[1]), self._to_meters(end[2]) if len(end) > 2 else 0.0)
            length = math.sqrt((end_m[0]-start_m[0])**2 + (end_m[1]-start_m[1])**2 + (end_m[2]-start_m[2])**2)
            info = {"start": start_m, "end": end_m, "length": length, "layer": layer,
                    "diameter": self._extract_pipe_diameter(entity, layer),
                    "material": self._determine_pipe_material(layer)}
            if self._is_pipe(layer):
                info["type"] = "pipe"
                info["pipe_system"] = self._determine_pipe_system(layer)
                self.entities["pipes"].append(info)
            elif self._is_wall(layer):
                info["type"] = "wall"
                self.entities["walls"].append(info)
        except Exception as e:
            logger.debug(f"Line error: {e}")

    def _extract_polyline_entity(self, entity):
        try:
            points = list(entity.get_points())
            layer = entity.dxf.layer.upper()
            if len(points) >= 3:
                points_m = [(self._to_meters(p[0]), self._to_meters(p[1])) for p in points]
                if self._is_room(layer):
                    info = {"points": points_m, "area": self._calculate_polygon_area(points_m),
                            "perimeter": self._calculate_perimeter(points_m), "layer": layer, "type": "room"}
                    self.entities["rooms"].append(info)
        except Exception as e:
            logger.debug(f"Polyline error: {e}")

    def _extract_circle_entity(self, entity):
        try:
            center = entity.dxf.center
            radius = self._to_meters(entity.dxf.radius)
            layer = entity.dxf.layer.upper()
            if self._is_tank("", layer):
                info = {"center": (self._to_meters(center[0]), self._to_meters(center[1])),
                        "radius": radius, "volume": self._calculate_tank_volume(radius),
                        "layer": layer, "type": "tank"}
                self.entities["tanks"].append(info)
        except Exception as e:
            logger.debug(f"Circle error: {e}")

    def _extract_text_entity(self, entity):
        try:
            info = {"text": entity.dxf.text,
                    "position": (self._to_meters(entity.dxf.insert[0]), self._to_meters(entity.dxf.insert[1])),
                    "layer": entity.dxf.layer.upper(), "type": "text"}
            self.entities["texts"].append(info)
        except Exception as e:
            logger.debug(f"Text error: {e}")

    def _extract_mtext_entity(self, entity):
        try:
            info = {"text": entity.text,
                    "position": (self._to_meters(entity.dxf.insert[0]), self._to_meters(entity.dxf.insert[1])),
                    "layer": entity.dxf.layer.upper(), "type": "text"}
            self.entities["texts"].append(info)
        except Exception as e:
            logger.debug(f"MText error: {e}")

    def _extract_block_attributes(self, entity):
        attributes = {}
        try:
            if hasattr(entity, "attribs"):
                for attrib in entity.attribs:
                    try:
                        attributes[attrib.dxf.tag] = attrib.dxf.text
                    except:
                        pass
        except:
            pass
        return attributes

    def _is_sprinkler(self, block_name, layer):
        if layer.startswith("FF-SPRIN") or block_name in ["S", "SP.", "PENDANT SP."]:
            return True
        keywords = ["SPRINKLER", "SPR", "HEAD", "PENDANT"]
        return any(k in block_name for k in keywords) or any(k in layer for k in keywords)

    def _is_pipe(self, layer):
        pipe_layers = ["FF-WBRA-LINE", "FF-WET-LINE", "FF-DRY-LINE", "FF-SPLN", "FF-NETWORK", "PIPE", "PIPING", "P-PIPE"]
        for prefix in pipe_layers:
            if layer == prefix or layer.startswith(prefix):
                return True
        return any(pattern in layer for pattern in ["FF-", "PIPE", "PIPING", "LINE"])

    def _is_wall(self, layer):
        return any(k in layer.upper() for k in ["WALL", "A-WALL"])

    def _is_room(self, layer):
        return any(k in layer.upper() for k in ["ROOM", "AREA", "ZONE"])

    def _is_pump(self, block_name, layer):
        if layer.startswith("FF-PUMP") or layer.startswith("PUMP"):
            return True
        return any(k in block_name for k in ["PUMP", "ELEC PUMP", "DIESEL PUMP", "JOCKEY PUMP"])

    def _is_valve(self, block_name, layer):
        return any(k in block_name for k in ["VALVE", "ZCV"]) or any(k in layer for k in ["VALVE", "ZCV"])

    def _is_tank(self, block_name, layer):
        return any(k in block_name for k in ["TANK"]) or any(k in layer for k in ["TANK", "STORAGE"])

    def _is_gas_system(self, block_name, layer):
        return any(k in block_name.upper() for k in ["FM-200", "FM200", "FM 200", "NOVEC", "INERGEN", "CO2"])

    def _is_hose_cabinet(self, block_name, layer):
        return any(k in block_name.upper() for k in ["FHC", "FIRE HOSE", "HOSE REEL", "HOSE CABINET"])

    def _is_fire_alarm(self, block_name, layer):
        return any(k in block_name.upper() for k in ["FIRE ALARM", "ALARM", "DETECTOR"])

    def _determine_k_factor(self, block_name):
        match = re.search(r"K[-_]?(\d+\.?\d*)", block_name.upper())
        return float(match.group(1)) if match else 5.6

    def _determine_sprinkler_type(self, block_name):
        if "PENDANT" in block_name or block_name == "S":
            return "pendant"
        elif "UPRIGHT" in block_name:
            return "upright"
        elif "SIDEWALL" in block_name:
            return "sidewall"
        return "standard"

    def _determine_pump_type(self, block_name):
        if "ELEC" in block_name:
            return "electric"
        elif "DIESEL" in block_name:
            return "diesel"
        elif "JOCKEY" in block_name:
            return "jockey"
        return "main"

    def _determine_gas_type(self, block_name):
        if "FM-200" in block_name or "FM200" in block_name or "FM 200" in block_name:
            return "FM-200"
        elif "NOVEC" in block_name:
            return "Novec 1230"
        elif "INERGEN" in block_name:
            return "Inergen"
        return "unknown"

    def _determine_pipe_system(self, layer):
        if "WET" in layer:
            return "wet"
        elif "DRY" in layer:
            return "dry"
        return "unknown"

    def _extract_pipe_diameter(self, entity, layer):
        match = re.search(r"(\d+)\s*(MM|DN|INCH)", layer.upper())
        if match:
            value = float(match.group(1))
            return value * 25.4 if "INCH" in match.group(2) else value
        return 50

    def _determine_pipe_material(self, layer):
        if "STEEL" in layer:
            return "steel"
        elif "CPVC" in layer:
            return "cpvc"
        return "steel"

    def _calculate_polygon_area(self, points):
        try:
            return Polygon(points).area
        except:
            return 0.0

    def _calculate_perimeter(self, points):
        try:
            return Polygon(points).length
        except:
            return 0.0

    def _calculate_tank_volume(self, radius):
        return math.pi * radius ** 2 * 2.5

    def _summarize_entities(self):
        summary = {
            "sprinklers": len(self.entities["sprinklers"]),
            "pipes": len(self.entities["pipes"]),
            "pumps": len(self.entities["pumps"]),
            "valves": len(self.entities["valves"]),
            "tanks": len(self.entities["tanks"]),
            "gas_systems": len(self.entities["gas_systems"]),
            "hose_cabinets": len(self.entities["hose_cabinets"]),
            "fire_alarm": len(self.entities["fire_alarm"]),
        }
        return ", ".join(f"{k}: {v}" for k, v in summary.items() if v > 0)
