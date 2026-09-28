# check: ILP solution depends only on S=A+Dis and T-S=Div-A (flow identities)
import numpy as np, itertools
import ilpy
rng=np.random.default_rng(0)
def build(T=8,n=12):
    nodes=[(t,i) for t in range(T) for i in range(n)]
    pos={v:rng.uniform(0,30,3) for v in nodes}
    edges=[]
    for t in range(T-1):
        for i in range(n):
            for j in range(n):
                d=np.linalg.norm(pos[(t,i)]-pos[(t+1,j)])
                if d<12: edges.append(((t,i),(t+1,j),float(np.clip(1.2-d/10+rng.normal(0,.1),0.48,1.0))))
    return nodes,edges
def solve(nodes,edges,A,Dis,Div):
    idx={};k=0
    for v in nodes:
        for nm in 'nadv': idx[(nm,v)]=k;k+=1
    for e in range(len(edges)): idx[('e',e)]=k;k+=1
    obj=ilpy.Objective(k)
    for v in nodes:
        obj.set_coefficient(idx[('a',v)],A);obj.set_coefficient(idx[('d',v)],Dis);obj.set_coefficient(idx[('v',v)],Div)
    for e,(s,t,p) in enumerate(edges): obj.set_coefficient(idx[('e',e)],-p)
    cs=ilpy.Constraints()
    for v in nodes:
        ins=[e for e,(s,t,p) in enumerate(edges) if t==v]; outs=[e for e,(s,t,p) in enumerate(edges) if s==v]
        c=ilpy.Constraint(); c.set_coefficient(idx[('a',v)],1)
        for e in ins: c.set_coefficient(idx[('e',e)],1)
        c.set_coefficient(idx[('n',v)],-1); c.set_relation(ilpy.Relation.Equal); c.set_value(0); cs.add(c)
        c=ilpy.Constraint(); c.set_coefficient(idx[('d',v)],1)
        for e in outs: c.set_coefficient(idx[('e',e)],1)
        c.set_coefficient(idx[('n',v)],-1); c.set_coefficient(idx[('v',v)],-1); c.set_relation(ilpy.Relation.Equal); c.set_value(0); cs.add(c)
        c=ilpy.Constraint(); c.set_coefficient(idx[('n',v)],1); c.set_coefficient(idx[('v',v)],-1); c.set_relation(ilpy.Relation.GreaterEqual); c.set_value(0); cs.add(c)
    s=ilpy.Solver(k,ilpy.VariableType.Binary,preference=ilpy.Preference.Scip)
    s.set_objective(obj); s.set_constraints(cs); sol=s.solve()
    sel=frozenset(v for v in nodes if sol[idx[('n',v)]]>.5); es=frozenset(e for e in range(len(edges)) if sol[idx[('e',e)]]>.5)
    nd=sum(sol[idx[('v',v)]]>.5 for v in nodes)
    return sel,es,nd
for seed in range(3):
    rng=np.random.default_rng(seed); nodes,edges=build()
    base=solve(nodes,edges,0,2,1.2); am=solve(nodes,edges,-0.2,2,1.2); d18=solve(nodes,edges,0,1.8,1.2)
    ap=solve(nodes,edges,0.4,2,1.2); combo=solve(nodes,edges,0,2.4,0.8)
    print(seed,'nodes base/A-0.2/Dis1.8/A0.4/Dis2.4Div0.8',len(base[0]),len(am[0]),len(d18[0]),len(ap[0]),len(combo[0]),
      '| A-.2==Dis1.8',am[0]==d18[0] and am[1]==d18[1],'| A.4==combo',ap[0]==combo[0] and ap[1]==combo[1],'| divs',base[2],ap[2])
def cost(nodes,edges,sol,S,T):
    sel,es,nd=sol; app=len(sel)-len(es)+0  # #appear = nodes - edges + 0 (no merges)
    return S*app + T*nd - sum(edges[e][2] for e in es)  # with #div counted in T; objective up to identity
for seed in (1,):
    rng=np.random.default_rng(seed); nodes,edges=build()
    am=solve(nodes,edges,-0.2,2,1.2); d18=solve(nodes,edges,0,1.8,1.2)
    print('seed1 obj A-.2 sol',round(cost(nodes,edges,am,1.8,3.0),9),'Dis1.8 sol',round(cost(nodes,edges,d18,1.8,3.0),9),'sym diff nodes',len(am[0]^d18[0]),'edges',len(am[1]^d18[1]))
