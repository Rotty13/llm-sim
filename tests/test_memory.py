from sim.memory.memory import MemoryStore, MemoryItem

def test_recall_basic():
    testword = "thirsty"
    ms = MemoryStore()
    ms.write(MemoryItem(t=1, kind="semantic", text="Rent due on 1st", importance=0.9))
    ms.write(MemoryItem(t=2, kind="autobio", text="Felt hungry", importance=0.4))
    out = ms.recall(testword, k=1)
    print(f"test: {testword} in {out[0].text} == {testword in out[0].text}")
    assert out and testword in out[0].text

if __name__ == "__main__":
    test_recall_basic()