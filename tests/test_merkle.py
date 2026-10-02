from backend.app.services.merkle import inclusion_proof, verify_inclusion, consistency_proof, verify_consistency

def test_inclusion():
    leaves=[f"event-{i}" for i in range(9)]
    for i,x in enumerate(leaves):
        p=inclusion_proof(leaves,i)
        assert verify_inclusion(x,p,p["root"])

def test_consistency():
    leaves=[f"event-{i}" for i in range(9)]
    for m in range(1,9):
        p=consistency_proof(leaves,m)
        assert verify_consistency(p["old_size"],p["new_size"],p["old_root"],p["new_root"],p["proof"]), (m,p)
