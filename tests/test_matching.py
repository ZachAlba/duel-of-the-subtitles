import pytest

from subtitle_toolkit.matching import extract_episode_number, find_matching_pairs


@pytest.mark.parametrize(
    "filename,expected",
    [
        ("ep1.mp4", 1),
        ("Episode 12.vtt", 12),
        ("Show.S02E05.mkv", 5),
        ("show s01e07 final.mp4", 7),
        ("[Group] Show - 12 [720p].mp4", 12),
        ("Show.1080p.E03.mp4", 3),
        ("Show (2020) - 04.mp4", 4),
        ("Show.03.x264.1080p.mp4", 3),
        ("no numbers here.mp4", None),
        ("Show.1080p.mp4", None),  # resolution only, no episode
    ],
)
def test_extract_episode_number(filename, expected):
    assert extract_episode_number(filename) == expected


def test_single_file_mode(tmp_path):
    video = tmp_path / "movie.mp4"
    sub = tmp_path / "movie.vtt"
    video.touch()
    sub.touch()
    pairs, unmatched = find_matching_pairs(str(video), str(sub))
    assert pairs == [(str(video), str(sub))]
    assert unmatched == []


def test_directory_mode_pairs_by_episode(tmp_path):
    videos = tmp_path / "videos"
    subs = tmp_path / "subs"
    videos.mkdir()
    subs.mkdir()
    for name in ["Show - 01 [1080p].mp4", "Show - 02 [1080p].mp4", "Show - 03 [1080p].mp4"]:
        (videos / name).touch()
    (subs / "episode 2.vtt").touch()
    (subs / "episode 3.vtt").touch()

    pairs, unmatched = find_matching_pairs(str(videos), str(subs))
    assert len(pairs) == 2
    assert pairs[0] == (str(videos / "Show - 02 [1080p].mp4"), str(subs / "episode 2.vtt"))
    assert pairs[1] == (str(videos / "Show - 03 [1080p].mp4"), str(subs / "episode 3.vtt"))
    assert unmatched == [str(videos / "Show - 01 [1080p].mp4")]


def test_mixed_file_and_directory_raises(tmp_path):
    video = tmp_path / "movie.mp4"
    video.touch()
    with pytest.raises(ValueError):
        find_matching_pairs(str(video), str(tmp_path))
