"""def get_nodes_names(self):
        body = self.dot.body
        node_names = []
        for line in body:
            match = re.search(r'\d+\s+\[label="(.*?)"\]', line)
            if match:
                node_name = match.group(1)
                node_names.append(node_name)
            else:
                match = re.search(r'"(.*?)"\s*->\s*"(.*?)"', line)
                if match:
                    node_names.append(match.group(1))
                    node_names.append(match.group(2))
                else:
                    match = re.search(r'"(.*?)"\s*\[.*?\]', line)
                    if match:
                        node_name = match.group(1)
                        node_names.append(node_name)
            match = re.search(r'\[label="(.*?)"\]', line)
            if match:
                node_name = match.group(1)
                node_names.append(node_name)
            else:
                match = re.search(r'(\w+)\s*\[.*?\]', line)
                if match:
                    node_name = match.group(1)
                    node_names.append(node_name)
        node_names = sorted(list(set(node_names)), key=lambda x: (int(re.search(r'\d+', x).group(0)) if re.search(r'\d+', x) else float('inf'), x))
        #print("node_names=", node_names)
        return node_names
"""

vertices = {3: '2'}
edges = {1: ['1', 'Узел 2']}
colors = {}

old_node_name = "Узел 2"
new_node_name = "3"

# Проверка на дубликат
for key, val in vertices.items():
    if new_node_name == val:
        print("дубликат")
for key, val in edges.items():
    if new_node_name == val[0] or new_node_name == val[1]:
        print("дубликат")  
for key, val in colors.items():
    print(val[1])
    if new_node_name == val[0]:
        print("дубликат")

# Замена имени на новое
for key, val in vertices.items():
    if val == old_node_name: 
        vertices[key] = new_node_name

for key, val in edges.items():
    if val[0] == old_node_name:
        edges[key] = [new_node_name, val[1]]
    elif val[1] == old_node_name:
        edges[key] = [val[0], new_node_name]

for key, val in colors.items():
    if val[0] == old_node_name:
        colors[key] = [new_node_name, val[1]]


print(vertices)
print(edges)
print(colors)

"""import re
node_names = ['Узел 2', 'Узел 1', "Узел 141", "1", "14", 'dfgdf']
node_names.sort(key=lambda x: (not x.startswith("Узел "), int(re.search(r'\d+', x).group(0)) if re.search(r'\d+', x) else float('inf'), x))
print(node_names)
"""
