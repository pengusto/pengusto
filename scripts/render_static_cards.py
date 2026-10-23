"""Regenerate the original static upstream/workbench cards; no network access."""
from pathlib import Path
assets=Path(__file__).resolve().parents[1]/"assets"
items=[('cookbook','Cookbook','Agent workflows','Experimental beta'),('you-got-this','You Got This','From goal to handoff','Execution skill'),('google-classroom-mcp','Classroom MCP','Teaching tools for agents','Beta · checks still open'),('tumo-full-submission-comments','Full Comments','Reveal hidden TUMO feedback','Browser script'),('lingono-cs50x','Lingono','Practice Japanese vocabulary','CS50x final project'),('vokabelrunde','Vokabelrunde','English → German practice','Python CLI'),('suika-2048-hosted','Suika 2048','A small fruit puzzle','Browser prototype'),('paper-glide-hosted','Paper Glide','Fly through a pixel city','Unity WebGL prototype'),('UnityEditorAI','UnityEditorAI','Natural language in Unity','Thesis prototype'),('spark-hedge-physics-2-community','Spark / Hedge Physics','Community physics playground','Independent mirror')]
from profile_projects import text
from profile_theme import dark_svg,light_svg
from html import escape
def static(stem,title,line,status,width=280,height=104):
    raw=f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img"><title>{escape(title+" — "+line)}</title><rect x="1" y="1" width="{width-2}" height="{height-2}" rx="12" fill="#191320" stroke="#49375f"/>'
    raw+=text(17,30,title,18,'#f1edf7',700)+text(width-17,30,'↗',18,'#bd93f9',anchor='end')+text(17,55,line,13)+text(17,81,status,10,'#bd93f9',mono=True)+'</svg>'
    for suffix,convert in [('',dark_svg),('-light',light_svg)]: (assets/(stem+suffix+'.svg')).write_text(convert(raw))
for name,title,line,status in items:static('workbench-'+name,title,line,status)
static('upstream-opencodex','OpenCodex','Readable login, even on narrow screens.','MERGED / #6388',420)
static('upstream-wallos','Wallos','Theme layout + resilient subscription lists.','2 FIXES ACCEPTED / VIA #1267',420)
