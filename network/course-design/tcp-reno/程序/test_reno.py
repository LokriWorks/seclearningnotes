import unittest
from reno_core import Reno, preset, random_run, SS, CA, FR

class RenoTests(unittest.TestCase):
    def grown(self, mode='course'):
        model = Reno(mode=mode)
        for _ in range(10): model.normal_rtt()
        return model
    def test_initial(self):
        r = Reno()
        self.assertEqual((r.cwnd,r.ssthresh,r.rtt,r.dupacks,r.state),(1,64,0,0,SS))
    def test_slow_start_and_ca(self):
        r = self.grown()
        self.assertEqual([x.cwnd for x in r.history], [1,2,4,8,16,32,64,65,66,67,68])
        self.assertEqual(r.state, CA)
    def test_first_two_dupacks_do_not_reduce(self):
        r = self.grown()
        r.duplicate_ack();r.duplicate_ack()
        self.assertEqual((r.cwnd,r.retransmissions,r.dupacks),(68,0,2))
    def test_third_dup_ack_course(self):
        r = self.grown()
        for _ in range(3):r.duplicate_ack()
        self.assertEqual((r.cwnd,r.ssthresh,r.state,r.fast_count),(34,34,FR,1))
    def test_third_dup_ack_standard(self):
        r = self.grown('standard')
        for _ in range(3):r.duplicate_ack()
        self.assertEqual((r.cwnd,r.ssthresh,r.state),(37,34,FR))
    def test_extra_dupacks_and_exit(self):
        r = self.grown()
        for _ in range(5):r.duplicate_ack()
        self.assertEqual((r.cwnd,r.retransmissions),(36,1))
        r.normal_rtt()
        self.assertEqual((r.cwnd,r.state,r.dupacks),(34,CA,0))
    def test_timeout(self):
        r = self.grown();r.timeout()
        self.assertEqual((r.cwnd,r.ssthresh,r.state,r.rtt),(1,34,SS,12))
    def test_timeout_during_fast_recovery(self):
        r=self.grown()
        for _ in range(3):r.duplicate_ack()
        r.timeout()
        self.assertEqual((r.cwnd,r.ssthresh,r.state,r.dupacks),(1,17,SS,0))
    def test_dupacks_reset_after_new_ack(self):
        r=Reno();r.duplicate_ack();r.normal_rtt();r.duplicate_ack()
        self.assertEqual(r.dupacks,1)
        self.assertEqual(r.retransmissions,0)
    def test_threshold_boundary_and_lower_bound(self):
        r=Reno(3);r.normal_rtt();r.normal_rtt()
        self.assertEqual((r.cwnd,r.state),(3,CA))
        r.timeout();self.assertEqual(r.ssthresh,2)
    def test_invalid_parameters(self):
        for threshold in [0,1,-1,2.5]:
            with self.assertRaises(ValueError):Reno(threshold)
        with self.assertRaises(ValueError):Reno(mode='unknown')
        with self.assertRaises(ValueError):random_run(-.1)
    def test_random_reproducible_and_invariants(self):
        self.assertEqual(random_run(.2,42)[1],random_run(.2,42)[1])
        for mode in ['course','standard']:
            for seed in range(50):
                r,_=random_run(.3,seed,300,mode)
                for row in r.history:
                    self.assertGreaterEqual(row.cwnd,1)
                    self.assertGreaterEqual(row.ssthresh,2)
                    self.assertIn(row.state,(SS,CA,FR))

if __name__=='__main__':unittest.main(verbosity=2)
