import pandas as pd, re

df = pd.read_csv('./data/LLM_Interview_Dataset-v2.csv')

P = re.compile(
    r'^(Candidate prompt|Could you explain this|Define and explain'
    r'|Interview Question|Please answer the following)\s*:\s*',
    re.IGNORECASE
)
norm = lambda q: P.sub('', str(q).strip()).strip().lower()
df['Core'] = df['Question'].apply(norm)
g = df.groupby(['Domain','Difficulty_Level'])['Core'].nunique().reset_index()

lines = [f'Total rows: {len(df)}']
for _, r in g.iterrows():
    lines.append(f"{r['Domain']} | {r['Difficulty_Level']} | {r['Core']} unique")

with open('scripts/stats.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
