from platform import node

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
      import os
      print(f"Current path {os.getcwd()}.")

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
               if len(t) == 2:
                  kwargs[t[0]]=t[1]
         self.add_link(link[1].Node1, link[1].Node2, **kwargs)

      nodes = pd.DataFrame(columns=['Node','Extra'])
      nodes_have_changed = False
      # TODO: deal with durations properly if --path option is provided
      if Path(node_csv).is_file():
         nodes_read = pd.read_csv(node_csv,sep=';',header=0,comment='#')
         nodes_temp = pd.concat([nodes, nodes_read]) # safety for wrong headers
         for link in links.iterrows(): 
            if link[1].Node1 not in nodes['Node'].values:
               if link[1].Node1 in nodes_temp['Node'].values:
                  nodes = pd.concat([nodes, nodes_temp[nodes_temp['Node'] == link[1].Node1]])
               else:
                  nodes = pd.concat([nodes, pd.DataFrame([[link[1].Node1, 'duration=1']], columns=['Node','Extra'])], ignore_index=True )
                  nodes_have_changed = True
            if link[1].Node2 not in nodes['Node'].values:
               if link[1].Node2 in nodes_temp['Node'].values:
                  nodes = pd.concat([nodes, nodes_temp[nodes_temp['Node'] == link[1].Node2]])
               else:
                  nodes = pd.concat([nodes, pd.DataFrame([[link[1].Node2, 'duration=1']], columns=['Node','Extra'])], ignore_index=True )
                  nodes_have_changed = True
         if len(set(nodes_read['Node'].values).difference(set(nodes['Node'].values))) > 0:
            nodes_have_changed = True
         if nodes_have_changed:
            click.echo(f"Nodes have changed. Parsing nodes from links and nodes and saving to {node_csv.replace('.csv', '_update.csv')}. Rename to use")
            nodes.to_csv(node_csv.replace('.csv', '_update.csv'), index=False, sep=';', header=True)
         nodes = nodes_read
      else: 
         click.echo(f"Node CSV file not found. Parsing nodes from links and saving to {node_csv}.")
         self.save_parsed_nodes(node_csv)  
         nodes_read = pd.read_csv(node_csv,sep=';',header=0,comment='#')
         nodes = pd.concat([nodes, nodes_read]) # safety for wrong headers

      for node in nodes.iterrows():
         kwargs={}
         node_extra = '' # default node type is normal node
         if not pd.isna(node[1].Extra): 
            extra = node[1].Extra.split(',')
            if len(extra) > 0: 
               for k in extra: 
                  t = k.split('=')
                  if len(t) == 2:
                     kwargs[t[0]]=t[1]
                  else:
                     node_extra = k
         node_name = node[1].Node
         match node_extra: 
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
   
   def get_node(self, node_name):
      for node in self.get_nodes():
         if node.get_name() == node_name:
            return node
      return None

   def get_children(self, node_name):
      children = []
      for edge in self.get_edges():
         if edge.get_source() == node_name:
            children.append(edge.get_destination())
      return children

   def get_parents(self, node_name):
      parents = []
      for edge in self.get_edges():
         if edge.get_destination() == node_name:
            parents.append(edge.get_source())
      return parents

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
         df = pd.concat([df, pd.DataFrame([[df_node, 'duration=1']], columns=['Node','Extra'])], ignore_index=True )
         # TODO: deal with durations properly if --path option is provided
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
      system_command = f'dot -Gsplines=true -Gratio="fill" -Goverlap=compress  -Tsvg {filename.replace(".png", ".dot")} -o {filename.replace(".png", ".svg")}'
      # del %1.svg      # dot -Gsplines=curved -Gratio="fill" -Goverlap=compress -Tsvg %1.dot -o%1.svg      import os
      os.system(system_command)
      #self.write_png(filename)
      system_command = f'inkscape.com {filename.replace(".png", ".svg")} --export-type=png --export-filename={filename}'
      os.system(system_command)  
      click.echo(f"Saved graph to {filename}")

   # find start and end nodes
   def find_start_end_nodes(self):
      nodes = [node.get_name() for node in self.get_nodes()]
      start_nodes = nodes.copy()
      end_nodes = nodes.copy()
      for edge in self.get_edges():
         start_node = edge.get_source()
         end_node = edge.get_destination()
         if end_node in start_nodes:
            start_nodes.remove(end_node)
         if start_node in end_nodes:
            end_nodes.remove(start_node)
      return start_nodes, end_nodes
   
   def compute_critical_path(self):
        start_nodes, end_nodes = self.find_start_end_nodes()
        duration = {}
        early_start = {}
        early_finish = {}
        late_start = {}
        late_finish = {}
        critical_nodes = {}

        # initialize duration and early_start for all nodes
        for node in self.get_nodes():
            node_name = node.get_name()
            duration[node_name] = int(node.get_attributes().get('duration', 1))
            early_start[node_name] = 0
            critical_nodes[node_name] = False

        # iterate through the graph in topological order to calculate early start times
        frontier = start_nodes.copy()
        while frontier:
            current_node = frontier.pop(0)
            current_duration = duration[current_node]
            for child in self.get_children(current_node):
                early_start[child] = max(early_start[child], early_start[current_node] + current_duration)
                frontier.append(child)

        max_early_finish = 0
        # update early_finish for all nodes
        for node in self.get_nodes():
            node_name = node.get_name()
            early_finish[node_name] = early_start[node_name] + duration[node_name]
            max_early_finish = max(max_early_finish, early_finish[node_name])

        for node in self.get_nodes():
            node_name = node.get_name()
            duration[node_name] = int(node.get_attributes().get('duration', 1))
            late_finish[node_name] = max_early_finish

        # get late finish
        frontier = end_nodes.copy()
        while frontier:
            current_node = frontier.pop(0)
            current_duration = duration[current_node]
            for parent in self.get_parents(current_node):
                late_finish[parent] = min(late_finish[parent], late_finish[current_node] - current_duration)
                frontier.append(parent)

        # compute late start
        for node in self.get_nodes():
            node_name = node.get_name()
            duration[node_name] = int(node.get_attributes().get('duration', 1))
            late_start[node_name] = late_finish[node_name] - duration[node_name]

        # make labels for each node with duration and early start
        for node in self.get_nodes():
            node_name = node.get_name()
            node.set_label(f"{node_name}\n|{duration[node_name]}|{{{early_start[node_name]}|{early_finish[node_name]}}}|{{{{{late_start[node_name]}}}|{{{late_finish[node_name]}}}}}")
            node.set_shape('record')
            if late_start[node_name] == early_start[node_name]:
               if late_finish[node_name] == early_finish[node_name]:
                  node.set_color('red')
                  critical_nodes[node_name] = True

        for edge in self.get_edges():
            source = edge.get_source()
            destination = edge.get_destination()
            if critical_nodes[source] and critical_nodes[destination]:
                edge.set_color('red')

   def is_cyclic(self) -> bool:
      """Detects if a directed graph has cycles using DFS."""
      visited = set()
      rec_stack = set()

      def dfs(node_name: str) -> bool:
         if node_name not in visited:
            visited.add(node_name)
            rec_stack.add(node_name)
            for child in self.get_children(node_name):
               if child not in visited and dfs(child):
                  return True
               elif child in rec_stack:
                  return True
         if node_name in rec_stack:
            rec_stack.remove(node_name)
         return False

      for node in self.get_nodes():
         node_name = node.get_name()
         if dfs(node_name):
               return True

      return False