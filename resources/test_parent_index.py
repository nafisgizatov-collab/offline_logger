import copy,random,unittest
from build_background_report import assign_parents

def reference(nodes,edges):
 bytrace={}
 for j,r in enumerate(nodes):bytrace.setdefault(r['trace'],[]).append(j)
 for i,n in enumerate(nodes):
  n['id']=i
  candidates=[j for j in bytrace.get(n['trace'],[]) for r in [nodes[j]] if j!=i and r['process']==n['process'] and r['start']<=n['start'] and r['end']>=n['end'] and (r['duration']>n['duration'] or j<i) and r['kind'] not in ('Длинная задача','SQL','Ожидание')]
  if candidates:n['parent']=min(candidates,key=lambda j:nodes[j]['duration']);n['relation']='Вложенность по trace и интервалу'
  elif n['trace'] in edges:
   trace,launch=edges[n['trace']];candidates=[j for j in bytrace.get(trace,[]) for r in [nodes[j]] if j!=i and r['start']<=launch<=r['end'] and r['kind'] not in ('Длинная задача','SQL','Ожидание')]
   if candidates:n['parent']=min(candidates,key=lambda j:nodes[j]['duration']);n['relation']='Инициатор по ruuid'

class ParentIndexTest(unittest.TestCase):
 def test_equivalence_overlaps_ties_processes_clipped_durations_and_edges(self):
  for seed in range(20):
   rng=random.Random(seed);nodes=[]
   for i in range(200):
    start=rng.randrange(20);end=start+rng.randrange(20)
    nodes.append(dict(start=start,end=end,duration=end-start+rng.randrange(4),trace=rng.choice(['a','b','c','']),process=rng.choice(['UI','Main']),kind=rng.choice(['БЛ','Метод','SQL','Ожидание','Длинная задача']),parent=None))
   nodes.sort(key=lambda n:(n['start'],-n['duration']));edges={'a':('b',10),'b':('a',5),'c':('c',12)}
   expected=copy.deepcopy(nodes);actual=copy.deepcopy(nodes);reference(expected,edges);assign_parents(actual,edges)
   self.assertEqual(actual,expected,'seed '+str(seed))
if __name__=='__main__':unittest.main()
