# Center-lakes location map (paper SI), lake 2511's tile highlighted gold.
# Inputs (edit paths below):
#   BedMachineGreenland-v6.nc  — NSIDC, https://doi.org/10.5067/GMEVBWFLWA7X
#   tile_attrs.json            — alongside this script (tile centers/flow angles)
#   labels_2019_volumes.geojson — center-lake outlines (drainage-classification dataset)
# Requires: xarray, netcdf4, geopandas, matplotlib, pyproj. Runtime ~2 min.
import xarray as xr, geopandas as gpd, json, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt, matplotlib.patches as mpatches, matplotlib.patheffects as pe
from matplotlib.colors import LightSource, ListedColormap
from pyproj import Transformer
D="/Users/jrines/stanford_gp/dissertation/defense/cinematic/source_data"  # EDIT: dir holding data/BedMachineGreenland-v6.nc and data/labels_2019_volumes.geojson
OUT=str(__import__("pathlib").Path(__file__).parent/"center_lakes_map_2511gold.png")
HL="2511"; GOLD="#f5b800"
x0,x1,y0,y1=-235e3,-85e3,-2295e3,-2025e3
km=1e-3
bm=xr.open_dataset(f"{D}/data/BedMachineGreenland-v6.nc")
win=bm.sel(x=slice(x0,x1),y=slice(y1,y0))
mask=win["mask"].values; surf=win["surface"].values.astype(float); X=win.x.values; Y=win.y.values
full=bm.isel(x=slice(None,None,20),y=slice(None,None,20)); fmask=full["mask"].values; FX=full.x.values; FY=full.y.values
ls=LightSource(azdeg=315,altdeg=45)
hs=ls.hillshade(surf,vert_exag=3,dx=150,dy=150)          # 0..1
ice=(mask==2)|(mask==3); land=(mask==1); ocean=(mask==0)
rgb=np.ones(surf.shape+(3,))
# ice: light grey-white hillshade; land: darker warm grey hillshade; ocean: pale blue
rgb[ice]=np.stack([0.72+0.28*hs[ice]]*3,axis=-1)
rgb[land]=np.stack([0.45+0.35*hs[land],0.43+0.35*hs[land],0.38+0.35*hs[land]],axis=-1)
rgb[ocean]=[0.82,0.89,0.95]
g=gpd.read_file(f"{D}/data/labels_2019_volumes.geojson").to_crs(3413)
tiles=json.load(open(str(__import__("pathlib").Path(__file__).parent/"tile_attrs.json"))); tr=Transformer.from_crs(4326,3413,always_xy=True)

def draw_lake(axis,new_id,lw):
    sub=g[g.new_id==new_id]
    for geom in sub.geometry:
        polys=[geom] if geom.geom_type=="Polygon" else list(geom.geoms)
        for pg in polys:
            xy=np.array(pg.exterior.coords)*km
            axis.add_patch(mpatches.Polygon(xy,closed=True,facecolor="#00c8ff",edgecolor="#003c8f",linewidth=lw,zorder=4))
    b=sub.total_bounds; print(new_id,"bounds km",np.round(b*km,1),"n",len(sub))

def top_edge_arrow(axis,cx,cy,c,s,lw,ms):
    """arrow along the visually-top edge of the rotated tile, pointing downstream (+u)."""
    P=lambda u,v:(cx+u*c-v*s,cy+u*s+v*c)
    edges=[(P(-half,half),P(half,half)),(P(-half,-half),P(half,-half))]   # the two along-flow edges
    (a,b)=max(edges,key=lambda e:(e[0][1]+e[1][1]))
    a=np.array(a); b=np.array(b); p0=a+0.25*(b-a); p1=a+0.75*(b-a)
    axis.annotate("",xy=p1*km,xytext=p0*km,arrowprops=dict(arrowstyle="-|>",lw=lw,color="black",mutation_scale=ms,shrinkA=0,shrinkB=0),zorder=5)

NORTH={"2411","2416","2511"}
def place_label(axis,lab,cx,cy,corners,fs,gap_km,halflen_km,c,s):
    """north group: just off the upstream end of the tile's top edge, no leader, text parallel to flow;
       2520: north corner; 1951: outside the NE edge, text parallel to flow."""
    C=np.array(corners)*km; kw=dict(fontsize=fs,fontweight="bold",zorder=6,path_effects=[pe.withStroke(linewidth=3,foreground="white")])
    rot=np.degrees(np.arctan2(s,c)); rot=(rot+180)%180
    if rot>90: rot-=180
    up=-np.array([c,s])                      # upstream = -x of the tile
    if lab not in ("2520","1951"):
        # right (upstream) edge of the box: u = -half; top end = larger y
        e=[C[0],C[3]]; top=max(e,key=lambda q:q[1]); bot=min(e,key=lambda q:q[1])
        frac={"2411":0.12,"2416":0.5,"2511":0.88}.get(lab,0.5)
        m=top+(bot-top)*frac; q=m+up*(gap_km+halflen_km)
        axis.text(q[0],q[1],lab,ha="center",va="center",rotation=rot,rotation_mode="anchor",**kw)
    elif lab=="2520":
        n=C[np.argmax(C[:,1])]; axis.text(n[0],n[1]+gap_km,lab,ha="center",va="bottom",rotation=rot,rotation_mode="anchor",**kw)
    elif lab=="1951":
        n=C[np.argmax(C[:,1])]; e=C[np.argmax(C[:,0])]; m=(n+e)/2; d=e-n; nrm=np.array([d[1],-d[0]]); nrm/=np.linalg.norm(nrm)
        if np.dot(nrm,m-C.mean(axis=0))<0: nrm=-nrm
        q=m+nrm*(gap_km+0.6*halflen_km)
        axis.text(q[0],q[1],lab,ha="center",va="center",rotation=rot,rotation_mode="anchor",**kw)
fig=plt.figure(figsize=(10.0,11.5)); ax=fig.add_axes([0.07,0.05,0.575,0.90])
ax.imshow(rgb,extent=(X[0]*km,X[-1]*km,Y[-1]*km,Y[0]*km),origin="upper",interpolation="bilinear",zorder=0)
surf_ice=np.where(ice,surf,np.nan)
cs=ax.contour(X*km,Y*km,surf_ice,levels=np.arange(250,2500,250),colors="#404040",linewidths=0.45,alpha=0.9,zorder=1)
ax.clabel(cs,levels=[500,1000,1500,2000],fmt="%d m",fontsize=7,colors="#303030",inline=True,inline_spacing=2)
half=7375.0   # 14.75 km analysis tile, same as the defense pipeline (domain_half_km)
offsets={"1910":(52,6),"1951":(52,10),"2520":(-52,-10),"2394":(52,4),"2411":(-52,14),"2416":(52,6),"2511":(52,-14)}
for k,a in tiles.items():
    lab=a["new_id"].replace("CW2019_","")
    cx,cy=tr.transform(a["lon"],a["lat"]); th=np.deg2rad(a["flow_angle_deg"]); c,s=np.cos(th),np.sin(th)
    corners=[(cx+u*c-v*s,cy+u*s+v*c) for u,v in [(-half,-half),(half,-half),(half,half),(-half,half)]]
    if lab==HL:
        ax.add_patch(mpatches.Polygon(np.array(corners)*km,closed=True,fill=False,edgecolor="black",linewidth=3.2,zorder=3))
        ax.add_patch(mpatches.Polygon(np.array(corners)*km,closed=True,fill=False,edgecolor=GOLD,linewidth=1.7,zorder=3.1))
    else:
        ax.add_patch(mpatches.Polygon(np.array(corners)*km,closed=True,fill=False,edgecolor="black",linewidth=1.1,zorder=3))
    top_edge_arrow(ax,cx,cy,c,s,1.4,9)
    draw_lake(ax,a["new_id"],0.9)
    place_label(ax,lab,cx,cy,corners,11,1.5,5.5,c,s)
ax.set_xlim(x0*km,x1*km); ax.set_ylim(y0*km,y1*km); ax.set_aspect("equal")
ax.set_xlabel("Easting (km, EPSG:3413)"); ax.set_ylabel("Northing (km, EPSG:3413)")
# graticule
def frame_label(xs,ys,txt,side):
    xs=np.array(xs)*km; ys=np.array(ys)*km
    ax.plot(xs,ys,color="k",lw=0.4,ls=":",alpha=0.55,zorder=2)
    if side=="left":
        j=np.argmin(np.abs(xs-x0*km))
        if y0*km<ys[j]<y1*km and abs(xs[j]-x0*km)<3: ax.text(x0*km+1.5,ys[j]+1,txt,fontsize=7,ha="left",va="bottom",alpha=0.9)
    else:
        j=np.argmin(np.abs(ys-y0*km))
        if x0*km<xs[j]<x1*km and abs(ys[j]-y0*km)<3: ax.text(xs[j]+1,y0*km+1.5,txt,fontsize=7,ha="left",va="bottom",alpha=0.9)
for lat in (69,70,71): lons=np.linspace(-58,-38,800); xs,ys=tr.transform(lons,np.full_like(lons,lat)); frame_label(xs,ys,f"{lat}°N","left")
for lon in (-52,-50,-48,-46): lats=np.linspace(65,75,800); xs,ys=tr.transform(np.full_like(lats,lon),lats); frame_label(xs,ys,f"{-lon}°W","bottom")
# scale bar (bottom right)
sx,sy=x1*km-40,y0*km+10
ax.plot([sx,sx+25],[sy,sy],color="k",lw=3,solid_capstyle="butt",zorder=6); ax.text(sx+12.5,sy+3,"25 km",ha="center",va="bottom",fontsize=8,zorder=6)
# legend (bottom left, over ocean)
h=[mpatches.Patch(facecolor="#00c8ff",edgecolor="#003c8f",lw=0.9,label="Center lake outline"),
   mpatches.Patch(facecolor="none",edgecolor="black",lw=1.1,label="15 km analysis tile, along-flow"),
   plt.Line2D([],[],color="#404040",lw=0.6,label="Surface elevation (250 m)")]
# inset top right
ins=fig.add_axes([0.4435,0.6485,0.20,0.30]); fbase=np.full(fmask.shape,np.nan); fbase[fmask==1]=1; fbase[fmask>=2]=2
ins.pcolormesh(FX*km,FY*km,fbase,cmap=ListedColormap(["#a89f8c","#f2f2f2"]),vmin=0.5,vmax=2.5,shading="auto",rasterized=True)
ins.add_patch(mpatches.Rectangle((x0*km,y0*km),(x1-x0)*km,(y1-y0)*km,fill=False,edgecolor="#d62728",lw=1.4))
ins.set_aspect("equal"); ins.set_xticks([]); ins.set_yticks([]); ins.set_facecolor("#d0e2ef")

ax.set_title("(a)",loc="left",fontsize=12,fontweight="bold")
# ---- zoom panels ----
zooms=[("(b)",["2411","2416","2511"],(-187e3,-2065e3),46e3),
       ("(c)",["2394"],(-183.4e3,-2148.3e3),30e3),
       ("(d)",["1951","2520"],(-156.5e3,-2247.8e3),30e3),
       ("(e)",["1910"],(-121.2e3,-2254.4e3),30e3)]
byid={a["new_id"].replace("CW2019_",""):a for a in tiles.values()}
for i,(let,ids,(zx,zy),L) in enumerate(zooms):
    zx0,zx1,zy0,zy1=zx-L/2,zx+L/2,zy-L/2,zy+L/2
    ax.add_patch(mpatches.Rectangle((zx0*km,zy0*km),L*km,L*km,fill=False,edgecolor="#555555",lw=0.8,ls="--",zorder=5))
    ax.text(zx0*km+1,zy1*km-1,let,fontsize=9,ha="left",va="top",color="#333333",zorder=6,path_effects=[pe.withStroke(linewidth=2.5,foreground="white")])
    za=fig.add_axes([0.715,0.05+(3-i)*0.235,0.236,0.205])
    w=bm.sel(x=slice(zx0-2e3,zx1+2e3),y=slice(zy1+2e3,zy0-2e3)); ws=w["surface"].values.astype(float); wm=w["mask"].values
    whs=ls.hillshade(ws,vert_exag=3,dx=150,dy=150); wrgb=np.ones(ws.shape+(3,)); wi=(wm==2)|(wm==3); wl=(wm==1)
    wrgb[wi]=np.stack([0.72+0.28*whs[wi]]*3,axis=-1); wrgb[wl]=np.stack([0.45+0.35*whs[wl],0.43+0.35*whs[wl],0.38+0.35*whs[wl]],axis=-1); wrgb[wm==0]=[0.82,0.89,0.95]
    za.imshow(wrgb,extent=(w.x.values[0]*km,w.x.values[-1]*km,w.y.values[-1]*km,w.y.values[0]*km),origin="upper",interpolation="bilinear")
    zc=za.contour(w.x.values*km,w.y.values*km,np.where(wi,ws,np.nan),levels=np.arange(250,2500,50),colors="#606060",linewidths=0.35,alpha=0.8)
    za.clabel(zc,levels=np.arange(250,2500,200),fmt="%d",fontsize=6,colors="#404040",inline=True)
    for lab in ids:
        a=byid[lab]; cx,cy=tr.transform(a["lon"],a["lat"]); th=np.deg2rad(a["flow_angle_deg"]); c,s=np.cos(th),np.sin(th)
        corners=[(cx+u*c-v*s,cy+u*s+v*c) for u,v in [(-half,-half),(half,-half),(half,half),(-half,half)]]
        if lab==HL:
            za.add_patch(mpatches.Polygon(np.array(corners)*km,closed=True,fill=False,edgecolor="black",linewidth=3.6,zorder=3))
            za.add_patch(mpatches.Polygon(np.array(corners)*km,closed=True,fill=False,edgecolor=GOLD,linewidth=2.0,zorder=3.1))
        else:
            za.add_patch(mpatches.Polygon(np.array(corners)*km,closed=True,fill=False,edgecolor="black",linewidth=1.2,zorder=3))
        top_edge_arrow(za,cx,cy,c,s,1.6,12)
        draw_lake(za,a["new_id"],1.0)
        place_label(za,lab,cx,cy,corners,10,1.0,3.8,c,s)
    za.set_xlim(zx0*km,zx1*km); za.set_ylim(zy0*km,zy1*km); za.set_aspect("equal")
    za.tick_params(labelsize=7); za.text(0.02,0.97,let,transform=za.transAxes,fontsize=11,fontweight="bold",ha="left",va="top",path_effects=[pe.withStroke(linewidth=3,foreground="white")],zorder=7)
    if i==3: za.set_xlabel("Easting (km)",fontsize=8)
    if i==1: za.set_ylabel("Northing (km)",fontsize=8)
    sb=5; za.plot([zx1*km-sb-2,zx1*km-2],[zy0*km+1.5,zy0*km+1.5],color="k",lw=2.5,solid_capstyle="butt"); za.text(zx1*km-2-sb/2,zy0*km+2.3,f"{sb} km",ha="center",va="bottom",fontsize=7)
h.append(plt.Line2D([],[],color="black",lw=1.4,marker=">",markevery=[1],label="Ice-flow direction (along tile top edge)"))
ax.legend(handles=h,loc="lower left",fontsize=8.5,framealpha=0.95)
fig.savefig(OUT,dpi=220,bbox_inches="tight"); print("saved",OUT)
