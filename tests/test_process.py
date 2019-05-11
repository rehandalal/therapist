from therapist.process import Process


class TestProcess(object):
    def test_process(self):
        p = Process("my-process")
        assert p.name == "my-process"
        assert p.description is None
        assert p.config == {}

        p = Process(
            "my-process", description="Process description", setting="my-setting"
        )
        assert p.name == "my-process"
        assert p.description == "Process description"
        assert p.config == {"setting": "my-setting"}

    def test_str(self):
        p = Process("my-process")
        assert str(p) == "my-process"

        p = Process("my-process", description="Process description")
        assert str(p) == "Process description"
