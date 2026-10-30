import unittest
from .project import DATA, SearchEngine, read_json, ranking_metrics, api_search, feedback

class ProjectTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=read_json(DATA/'clean.json'); cls.engine=SearchEngine(cls.rows)
    def test_groups_do_not_overlap(self):
        groups=[{r['author'] for r in self.rows if r['split']==s} for s in ('train','validation','test')]
        self.assertFalse(groups[0]&groups[1] or groups[1]&groups[2] or groups[0]&groups[2])
    def test_clean_counts_and_rights(self):
        self.assertEqual(len(self.rows),36)
        self.assertEqual(len({r['sha256'] for r in self.rows}),36)
        self.assertTrue(all(r['rights_status']=='demo_allowed' for r in self.rows))
    def test_perfect_ranking(self):
        self.assertEqual(ranking_metrics([2,1,0],[2,1,0],2),{'ndcg':1.0,'recall':1.0})
    def test_empty_ranking(self):
        self.assertEqual(ranking_metrics([],[2,1],2),{'ndcg':0.0,'recall':0.0})
    def test_wrong_order(self):
        self.assertAlmostEqual(ranking_metrics([1,2,0],[2,1,0],2)['ndcg'],0.79670758,places=6)
    def test_array_payload(self):
        self.assertEqual(api_search(self.engine,[])[0],400)
    def test_synonym_lookup(self):
        self.assertEqual(self.engine.search('саксофон лаконичный','baseline'),[])
        self.assertEqual(self.engine.search('саксофон лаконичный','improved')[0]['genre'],'джаз')
    def test_invalid_input(self):
        for query in ('','а'*301,None,42): self.assertEqual(api_search(self.engine,{'query':query})[0],400)
    def test_unknown_language(self):
        self.assertEqual(api_search(self.engine,{'query':'jazz minimalist'})[1]['status'],'no_matches')
    def test_fallback_visible(self):
        self.assertEqual(api_search(self.engine,{'query':'джаз'},True)[1]['status'],'fallback')
    def test_feedback_does_not_train(self):
        result=feedback('P003','correct','designer_demo','детализация')
        self.assertEqual(result['status'],'pending_review'); self.assertFalse(result['model_updated'])
    def test_idf_ignores_test(self):
        altered=[dict(r,description='совершенноновоеслово') if r['split']=='test' else r for r in self.rows]
        self.assertEqual(self.engine.idf,SearchEngine(altered).idf)
    def test_rights_filter_defense(self):
        rows=[dict(r,rights_status='unknown') if r['id']=='P003' else r for r in self.rows]
        self.assertNotIn('P003',[r['id'] for r in SearchEngine(rows).search('джаз минимализм','improved')])
    def test_source_required(self):
        rows=[dict(r,source='') if r['id']=='P003' else r for r in self.rows]
        self.assertNotIn('P003',[r['id'] for r in SearchEngine(rows).search('джаз минимализм','improved')])

if __name__=='__main__': unittest.main()
