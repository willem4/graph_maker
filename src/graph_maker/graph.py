import pydot 
from typing import Any
from pathlib import Path
import click
import os 

class Graph(pydot.Dot): 
   # initialises an empty graph
   def __init__(self, *args: Any, **kwargs: Any) -> None: 
      super().__init__(*args, **kwargs)

   def from_csv(self, link_csv, node_csv=''): 
      import pandas as pd

      links = pd.DataFrame(columns=['Node1','Node2','Extra'])
      if Path(link_csv).is_file():
         links_read = pd.read_csv(link_csv,sep=';',header=0,comment='#')
         links = pd.concat([links, links_read]) # safety for wrong headers
      else: 
         raise FileNotFoundError("Link CSV file not found.")

      # find links and nodes
      nodes_from_links = []
      for link in links.iterrows(): 
         kwargs={}
         if not pd.isna(link[1].Extra): 
            r = link[1].Extra.split(',')
            for k in r: 
               t = k.split('=')
               kwargs[t[0]]=t[1]
         self.add_link(link[1].Node1, link[1].Node2, **kwargs)

      nodes = pd.DataFrame(columns=['Node','Extra'])
      if Path(node_csv).is_file():
         nodes_read = pd.read_csv(node_csv,sep=';',header=0,comment='#')
         nodes = pd.concat([nodes, nodes_read]) # safety for wrong headers
      else: 
         click.echo(f"Node CSV file not found. Parsing nodes from links and saving to {node_csv}.")
         self.save_parsed_nodes(node_csv)  
         nodes_read = pd.read_csv(node_csv,sep=';',header=0,comment='#')
         nodes = pd.concat([nodes, nodes_read]) # safety for wrong headers

      for node in nodes.iterrows():
         kwargs={}
         if not pd.isna(node[1].Extra): 
            extra = node[1].Extra
         node_name = node[1].Node
         match extra: 
            case "Completed": 
               self.add_completed(node_name, **kwargs)
            case "Failed": 
               self.add_failed(node_name, **kwargs)
            case "Available": 
               self.add_available(node_name, **kwargs)
            case "Decision": 
               self.add_decision(node_name, **kwargs)
            case "Input": 
               self.add_input(node_name, **kwargs)
            case "Research Question": 
               self.add_research_question(node_name, **kwargs)     
            case _: 
               self.add_node(node_name, **kwargs)         

   def save_parsed_nodes(self, filename):
      import pandas as pd
      df = pd.DataFrame(columns=['Node','Extra'])
      nodes = [] # As a list not a set to preserve order
      for edge in list(self.obj_dict["edges"].keys()):
         node1, node2 = self.obj_dict["edges"][edge][0]["points"]
         if node1 not in nodes:
            nodes.append(node1)
         if node2 not in nodes:
            nodes.append(node2)
      for df_node in nodes:
         df = pd.concat([df, pd.DataFrame([[df_node, '']], columns=['Node','Extra'])], ignore_index=True )
      df.to_csv(filename, index=False, sep=';', header=True)

   def add_completed(self, node_name, *args: Any, **kwargs: Any):
      kwargs["shape"]="rectangle" 
      kwargs["fillcolor"]="green"
      kwargs["style"]="filled"
      super().add_node(pydot.Node(node_name, *args, **kwargs))

   def add_failed(self, node_name, *args: Any, **kwargs: Any):
      kwargs["shape"]="rectangle" 
      kwargs["fillcolor"]="red"
      kwargs["style"]="filled"
      super().add_node(pydot.Node(node_name, *args, **kwargs))

   def add_available(self, node_name, *args: Any, **kwargs: Any):
      kwargs["shape"]="rectangle" 
      kwargs["fillcolor"]="lightgreen"
      kwargs["style"]="filled"
      super().add_node(pydot.Node(node_name, *args, **kwargs))

   def add_node(self, node_name, *args: Any, **kwargs: Any):
      kwargs["shape"]="rectangle" 
      super().add_node(pydot.Node(node_name, *args, **kwargs))

   def add_decision(self, node_name, *args: Any, **kwargs: Any):
      kwargs["shape"]="diamond" 
      kwargs["fillcolor"]="yellow"
      kwargs["style"]="filled"
      super().add_node(pydot.Node(node_name, *args, **kwargs))

   def add_research_question(self, node_name, *args: Any, **kwargs: Any):
      kwargs["shape"]="rectangle" 
      kwargs["fillcolor"]="orange"
      kwargs["style"]="filled"
      super().add_node(pydot.Node(node_name, *args, **kwargs))

   def add_input(self, node_name, *args: Any, **kwargs: Any):
      kwargs["shape"]="parallelogram" 
      kwargs["fillcolor"]="orange"
      kwargs["style"]="filled"
      super().add_node(pydot.Node(node_name, *args, **kwargs))

   # add link between nodes
   def add_link(self, node1_name, node2_name, *args: Any, **kwargs: Any):
      super().add_edge(pydot.Edge(node1_name, node2_name, *args, **kwargs))

   # save graph as .dot file
   def save_as_dot(self, filename):
      self.write_raw(filename)
      click.echo(f"Saved graph to {filename}")

   # save graph as .png file
   def save_as_png(self, filename):
      if not Path(filename.replace('.png', '.dot')).is_file():
         click.echo(f"DOT file {filename.replace('.png', '.dot')} not found. Cannot save as PNG.")
         return
      system_command = f'dot -Gsplines=curved -Gratio="fill" -Goverlap=compress  -Tsvg {filename.replace(".png", ".dot")} -o {filename.replace(".png", ".svg")}'
      # del %1.svg      # dot -Gsplines=curved -Gratio="fill" -Goverlap=compress -Tsvg %1.dot -o%1.svg      import os
      os.system(system_command)
      #self.write_png(filename)
      system_command = f'inkscape.com {filename.replace(".png", ".svg")} --export-type=png --export-filename={filename}'
      os.system(system_command)  
      click.echo(f"Saved graph to {filename}")