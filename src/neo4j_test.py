# Institution:HUST
# Author:Xiding Luo
# Time: 2021/11/20 15:35

from py2neo import Node, Relationship, Graph, NodeMatcher, RelationshipMatcher
import csv

# 数据库
graph = Graph('http://localhost:7474', auth=("neo4j", "010615"))


def CreateNode(m_graph, m_label, m_attrs):
    m_n = '_.name=' + "\'" + m_attrs['name'] + "\'"
    matcher = NodeMatcher(m_graph)
    re_value = matcher.match(m_label).where(m_n).first()
    if re_value is None:
        m_node = Node(m_label, **m_attrs)
        n = graph.create(m_node)
        return n
    return None


def MatchNode(m_graph, m_label, m_attrs):
    m_n = '_.name='+"\'"+m_attrs['name']+"\'"
    matcher = NodeMatcher(m_graph)
    re_value = matcher.match(m_label).where(m_n).first()
    return re_value


def CreateRelationship(m_graph, m_label1, m_attrs1, m_label2, m_attrs2, m_r_name):
    reValue1 = MatchNode(m_graph, m_label1, m_attrs1)
    revalue2 = MatchNode(m_graph, m_label2, m_attrs2)
    if reValue1 is None or revalue2 is None:
        return False
    m_r = Relationship(reValue1, m_r_name, revalue2)
    n = graph.create(m_r)
    return n


def CreateGraph():
    with open('movie_data.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        movieName = [row[0] for row in reader]

    with open('movie_data.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        directors = [row[5] for row in reader]

    with open('movie_data.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        country = [row[8] for row in reader]

    with open('movie_data.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        actor = [row[6] for row in reader]

    with open('movie_data.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        type1 = [row[7] for row in reader]

    label1 = "电影"
    label2 = "导演"
    label3 = "国家"
    label4 = "演员"
    label5 = "类型"

    #取出所有演员
    actors = []
    for i in range(1, len(actor)):
        lst1 = actor[i].split('/')
        if len(lst1) < 3:
            m = len(lst1)
        else:
            m = 3
        for j in range(0, m):
            lst2 = lst1[j].split()
            actors.append(lst2[0])

    # 取出所有国家
    countries = []
    for i in range(1, 251):
        lst1 = country[i].split('/')
        for j in range(0, len(lst1)):
            lst2 = lst1[j].split()
            countries.append(lst2[0])

    # 取出所有类型
    types = []
    for i in range(1, 251):
        lst1 = type1[i].split('/')
        for j in range(0, len(lst1)):
            lst2 = lst1[j].split()
            types.append(lst2[0])

    # 创建所有电影节点
    for i in range(1, 251):
        attrs1 = {"name": movieName[i]}
        CreateNode(graph, label1, attrs1)

    # 创建所有导演节点
    for i in range(1, 251):
        attrs2 = {"name": directors[i]}
        CreateNode(graph, label2, attrs2)

    # 创建所有国家节点
    for i in range(0, len(countries)):
        attrs3 = {"name": countries[i]}
        CreateNode(graph, label3, attrs3)

    # 创建所有演员节点（每一个电影取三个演员）
    for i in range(0, len(actors)):
        attrs4 = {"name": actors[i]}
        CreateNode(graph, label4, attrs4)

    # 创建所有类型节点
    for i in range(0, len(types)):
        attrs5 = {"name": types[i]}
        CreateNode(graph, label5, attrs5)

    # 创建电影与导演的关系
    for i in range(1, 251):
        attrs1 = {"name": movieName[i]}
        attrs2 = {"name": directors[i]}
        reValue = CreateRelationship(graph, label1, attrs1, label2, attrs2, m_r_name='导演')

    # 创建电影与国家的关系
    # temp表示当前国家位置
    temp = 0
    for i in range(1,251):
        attrs1 = {"name": movieName[i]}
        lst1 = country[i].split('/')
        for j in range(0, len(lst1)):
            attrs3 = {"name": countries[temp]}
            reValue = CreateRelationship(graph, label1, attrs1, label3, attrs3, m_r_name='国家')
            temp = temp + 1

    # 创建电影与演员的关系
    # temp表示当前电影的位置
    temp = 0
    for i in range(1, 251):
        attrs1 = {"name": movieName[i]}
        lst1 = actor[i].split('/')
        if len(lst1) < 3:
            m = len(lst1)
        else:
            m = 3
        for j in range(0, m):
            attrs4 = {"name": actors[temp]}
            reValue = CreateRelationship(graph, label1, attrs1, label4, attrs4, m_r_name='演员')
            temp = temp + 1

    # 创建电影与类型的关系
    # temp表示当前类型位置
    temp = 0
    for i in range(1, 251):
        attrs1 = {"name": movieName[i]}
        lst1 = type1[i].split('/')
        for j in range(0, len(lst1)):
            attrs5 = {"name": types[temp]}
            reValue = CreateRelationship(graph, label1, attrs1, label5, attrs5, m_r_name='类型')
            temp = temp + 1


if __name__ == '__main__':
    CreateGraph()