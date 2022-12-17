import customtkinter
from tkintermapview import TkinterMapView
from shapely.geometry import MultiPoint, Point
from PIL import Image, ImageTk
import pandas as pd
import geopandas as gpd
import os

customtkinter.set_default_color_theme("blue")

class App(customtkinter.CTk):

    APP_NAME = "Skynet"
    WIDTH = 800
    HEIGHT = 500

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title(App.APP_NAME)
        self.geometry(str(App.WIDTH) + "x" + str(App.HEIGHT))
        self.minsize(App.WIDTH, App.HEIGHT)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.bind("<Command-q>", self.on_closing)
        self.bind("<Command-w>", self.on_closing)
        self.createcommand('tk::mac::Quit', self.on_closing)

        self.marker_list = []
        self.area_polygon = None
        self.buildings_extracted = []

        # ============ create two CTkFrames ============

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frame_left = customtkinter.CTkFrame(master=self, width=150, corner_radius=0, fg_color=None)
        self.frame_left.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")

        self.frame_right = customtkinter.CTkFrame(master=self, corner_radius=0)
        self.frame_right.grid(row=0, column=1, rowspan=1, pady=0, padx=0, sticky="nsew")

        # ============ frame_left ============

        self.frame_left.grid_rowconfigure(4, weight=1)

        self.map_label = customtkinter.CTkLabel(self.frame_left, text="Tile Server:", anchor="w")
        self.map_label.grid(row=2, column=0, padx=(20, 20), pady=(20, 0))
        self.map_option_menu = customtkinter.CTkOptionMenu(self.frame_left, values=["OpenStreetMap", "Google normal", "Google satellite"],
                                                                       command=self.change_map)
        self.map_option_menu.grid(row=5, column=0, padx=(20, 20), pady=(30, 20))

        self.clear_markers_button = customtkinter.CTkButton(master=self.frame_left,
                                                            text="Clear Markers",
                                                            command=self.clear_marker_event)
        self.clear_markers_button.grid(pady=(20, 0), padx=(20, 20), row=1, column=0)

        self.clear_markers_button = customtkinter.CTkButton(master=self.frame_left,
                                                            text="Extract buildings",
                                                            command=self.extract_buildings_event)
        self.clear_markers_button.grid(pady=(20, 0), padx=(20, 20), row=2, column=0)

        self.clear_markers_button = customtkinter.CTkButton(master=self.frame_left,
                                                            text="Clear buildings",
                                                            command=self.clear_buildings_event)
        self.clear_markers_button.grid(pady=(20, 0), padx=(20, 20), row=3, column=0)
        
        # ============ frame_right ============

        self.frame_right.grid_rowconfigure(1, weight=1)
        self.frame_right.grid_rowconfigure(0, weight=0)
        self.frame_right.grid_columnconfigure(0, weight=1)
        self.frame_right.grid_columnconfigure(1, weight=0)
        self.frame_right.grid_columnconfigure(2, weight=1)

        self.map_widget = TkinterMapView(self.frame_right, corner_radius=0)
        self.map_widget.grid(row=1, rowspan=1, column=0, columnspan=3, sticky="nswe", padx=(0, 0), pady=(0, 0))

        # Set default values
        self.map_widget.set_address("Milan")
        self.map_option_menu.set("OpenStreetMap")

        def add_marker_event(coords):
            print("Add marker:", coords)
            marker_icon = ImageTk.PhotoImage(Image.open("GUI/utils/icon.svg").resize((10, 10)))
            new_marker = self.map_widget.set_marker(coords[0], coords[1], icon = marker_icon)
            self.marker_list.append(new_marker)

            if self.area_polygon is not None:
                self.area_polygon.delete()
            
            convex_hull = MultiPoint([marker.position for marker in self.marker_list]).convex_hull
        
            for marker in self.marker_list:
                if convex_hull.buffer(-1e-9).contains(Point(marker.position)):
                    marker.delete()
                    self.marker_list.remove(marker)
            
            if convex_hull.geom_type == 'Polygon':
                self.area_polygon = self.map_widget.set_polygon(convex_hull.exterior.coords,
                                    fill_color=None,outline_color="red", border_width=4,
                                    name="area")


        self.map_widget.add_left_click_map_command(add_marker_event)


    def clear_marker_event(self):
        for marker in self.marker_list:
            marker.delete()
        self.marker_list = []

        if self.area_polygon is not None:
            self.area_polygon.delete()
            self.area_polygon = None

    def generate_coverage_polygon(self):
        if self.area_polygon is None:
            raise Exception("Coverage polygon does not exists!")
        else:
            # Note that the position is reversed due to opposite defaults of geopandas and tkinter
            coverage_poly = MultiPoint([marker.position[::-1] for marker in self.marker_list]).convex_hull
            gpd.GeoDataFrame(pd.DataFrame([{"id": "0"}]), geometry=[coverage_poly],crs="EPSG:4326").to_file("test/coverage.shp")

    def clear_buildings_event(self):
        for building in self.buildings_extracted:
            building.delete()
        self.buildings_extracted = []

    def extract_buildings_event(self):
        self.generate_coverage_polygon()
        if len(self.buildings_extracted):
            self.clear_buildings_event()
        os.system("python src/main.py -i test/coverage.shp")
        buildings_gdf = gpd.read_file("test/extraction.shp")
        for building in buildings_gdf.geometry:
            self.buildings_extracted.append(self.map_widget.set_polygon([coord[::-1] for coord in building.exterior.coords],
                                            fill_color="blue",outline_color="red", border_width=1,
                                            name="area"))

    def change_appearance_mode(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_map(self, new_map: str):
        if new_map == "OpenStreetMap":
            self.map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")
        elif new_map == "Google normal":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        elif new_map == "Google satellite":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)

    def on_closing(self, event=0):
        self.destroy()

    def start(self):
        self.mainloop()


if __name__ == "__main__":
    app = App()
    app.start()