import os
import pandas
import pytest

from pathlib import Path

import orchestrator

FAKE_CSV_FILE = 'tests/fake_metrics_output.csv'


@pytest.fixture(scope='session')
def cleanup_files():
    yield
    file = Path(FAKE_CSV_FILE)
    if file.exists():
        os.remove(file)


def fake_conditional_function(file: str):
    return True


def test_get_concat_metrics_by_network_when_network_is_empty(caplog):
    folder = orchestrator._get_directories_from_folder('./tests/fake_folder')
    networks = []
    conditional_funct = fake_conditional_function

    total_metrics = orchestrator._get_concat_metrics_by_network(folder, networks, conditional_funct)

    assert 'The list of networks is empty' in caplog.text
    assert total_metrics == []

def test_get_concat_metrics_by_network_when_conditional_funct_is_not_defined(caplog):
    folder = orchestrator._get_directories_from_folder('./tests/fake_folder')
    networks = ['anvil', 'geth', 'geth', 'hardhat']
    conditional_funct = None

    total_metrics = orchestrator._get_concat_metrics_by_network(folder, networks, conditional_funct)

    assert 'The conditional_function is not valid' in caplog.text
    assert total_metrics == []

def test_get_concat_metrics_by_network_when_conditional_funct_is_empty(caplog):
    folder = orchestrator._get_directories_from_folder('./tests/fake_folder')
    networks = ['anvil', 'geth', 'geth', 'hardhat']
    conditional_funct = ''

    total_metrics = orchestrator._get_concat_metrics_by_network(folder, networks, conditional_funct)

    assert 'The conditional_function is not valid' in caplog.text
    assert total_metrics == []


def test_get_concat_metrics_by_network_when_anvil_network_contains_valid_rosbag_metrics():
    """
    timestamp,cpu_pct,mem_rss_bytes,mem_pct,disk_read_bytes,disk_write_bytes
    2026-06-25 10:47:21,120.00,11124736,0.03,0,16384
    2026-06-25 10:47:22,192.16,191463424,0.58,704512,348160
    2026-06-25 10:47:23,18.84,202129408,0.62,94208,11472896
    2026-06-25 10:47:24,42.57,220807168,0.67,0,0
    2026-06-25 10:47:25,42.61,220880896,0.67,0,4096
    2026-06-25 10:47:26,34.64,220983296,0.67,0,0
    2026-06-25 10:47:27,41.62,221048832,0.68,0,0
    2026-06-25 10:47:28,33.65,221065216,0.68,0,0
    2026-06-25 10:47:29,36.66,221114368,0.68,0,0
    2026-06-25 10:47:30,39.54,221155328,0.68,0,0
    2026-06-25 10:47:31,34.71,221212672,0.68,0,4096
    2026-06-25 10:47:32,39.60,221261824,0.68,0,0
    2026-06-25 10:47:33,36.71,221278208,0.68,0,0
    2026-06-25 10:47:34,38.68,221278208,0.68,0,0
    2026-06-25 10:47:35,35.61,221306880,0.68,0,0
    2026-06-25 10:47:36,39.67,221331456,0.68,0,0
    2026-06-25 10:47:38,36.66,221347840,0.68,0,4096
    2026-06-25 10:47:39,41.60,221351936,0.68,0,0
    2026-06-25 10:47:40,38.65,221356032,0.68,0,0
    2026-06-25 10:47:41,41.60,221356032,0.68,0,0
    2026-06-25 10:47:42,39.59,221356032,0.68,0,0
    2026-06-25 10:47:43,0.00,221356032,0.68,0,0
    2026-06-25 10:47:44,0.00,221356032,0.68,0,0
    2026-06-25 10:47:45,0.00,221356032,0.68,0,0
    2026-06-25 10:47:46,0.00,221356032,0.68,0,0
    2026-06-25 10:47:47,1.97,221356032,0.68,0,0

    Means: 26.00,39.51,221356032.00,0.65,798720.00,11849728.00
    """
    folder = orchestrator._get_directories_from_folder('./tests/fake_folder/')
    networks = ['anvil']
    conditional_funct = fake_conditional_function

    total_metrics = orchestrator._get_concat_metrics_by_network(folder, networks, conditional_funct)

    assert total_metrics['anvil']['timestamp'].mean().round(2) == 26
    assert total_metrics['anvil']['cpu_pct'].mean().round(2) == 39.51
    assert total_metrics['anvil']['mem_rss_bytes'].mean().round(2) == 221356032.00
    assert total_metrics['anvil']['mem_pct'].mean().round(2) == 0.65
    assert total_metrics['anvil']['disk_read_bytes'].mean().round(2) == 798720.00
    assert total_metrics['anvil']['disk_write_bytes'].mean().round(2) == 11849728.00

def test_get_concat_metrics_by_network_when_geth_network_contains_valid_rosbag_metrics():
    """
    timestamp,cpu_pct,mem_rss_bytes,mem_pct,disk_read_bytes,disk_write_bytes
    2026-06-26 10:50:16,0.00,11173888,0.03,0,16384
    2026-06-26 10:50:17,192.24,191000576,0.58,0,348160
    2026-06-26 10:50:18,8.93,201220096,0.61,0,11472896
    2026-06-26 10:50:19,45.62,222150656,0.68,0,0
    2026-06-26 10:50:20,38.69,222216192,0.68,0,4096
    2026-06-26 10:50:21,40.61,222306304,0.68,0,0
    2026-06-26 10:50:22,38.69,222388224,0.68,0,0
    2026-06-26 10:50:23,34.78,222425088,0.68,0,0
    2026-06-26 10:50:24,39.72,222482432,0.68,0,0
    2026-06-26 10:50:25,34.91,222494720,0.68,0,0
    2026-06-26 10:50:26,38.74,222543872,0.68,0,4096
    2026-06-26 10:50:27,32.74,222572544,0.68,0,0
    2026-06-26 10:50:28,40.64,222625792,0.68,0,0
    2026-06-26 10:50:29,40.68,222633984,0.68,0,0
    2026-06-26 10:50:30,34.68,222642176,0.68,0,0
    2026-06-26 10:50:31,37.61,222642176,0.68,0,0
    2026-06-26 10:50:32,36.75,222674944,0.68,0,0
    2026-06-26 10:50:34,36.68,222679040,0.68,0,4096
    2026-06-26 10:50:35,40.58,222683136,0.68,0,0
    2026-06-26 10:50:36,40.71,222703616,0.68,0,0
    2026-06-26 10:50:37,40.71,222703616,0.68,0,0
    2026-06-26 10:50:38,38.79,222703616,0.68,0,0
    2026-06-26 10:50:39,0.00,222703616,0.68,0,0
    2026-06-26 10:50:40,0.00,222703616,0.68,0,0
    2026-06-26 10:50:41,0.00,222703616,0.68,0,0
    2026-06-26 10:50:42,0.00,222703616,0.68,0,0
    2026-06-26 10:50:43,2.97,222703616,0.68,0,0

    Means: 27.00,34.68,222703616.00,0.65,0.00,11849728.00
    """
    folder = orchestrator._get_directories_from_folder('./tests/fake_folder/')
    networks = ['geth']
    conditional_funct = fake_conditional_function

    total_metrics = orchestrator._get_concat_metrics_by_network(folder, networks, conditional_funct)

    assert total_metrics['geth']['timestamp'].mean().round(2) == 27
    assert total_metrics['geth']['cpu_pct'].mean().round(2) == 34.68
    assert total_metrics['geth']['mem_rss_bytes'].mean().round(2) == 222703616.00
    assert total_metrics['geth']['mem_pct'].mean().round(2) == 0.65
    assert total_metrics['geth']['disk_read_bytes'].mean().round(2) == 0.00
    assert total_metrics['geth']['disk_write_bytes'].mean().round(2) == 11849728.00

def test_get_concat_metrics_by_network_when_anvil_and_geth_networks_contains_valid_rosbag_metrics():
    """
    anvil
    timestamp,cpu_pct,mem_rss_bytes,mem_pct,disk_read_bytes,disk_write_bytes
    2026-06-25 10:47:21,120.00,11124736,0.03,0,16384
    2026-06-25 10:47:22,192.16,191463424,0.58,704512,348160
    2026-06-25 10:47:23,18.84,202129408,0.62,94208,11472896
    2026-06-25 10:47:24,42.57,220807168,0.67,0,0
    2026-06-25 10:47:25,42.61,220880896,0.67,0,4096
    2026-06-25 10:47:26,34.64,220983296,0.67,0,0
    2026-06-25 10:47:27,41.62,221048832,0.68,0,0
    2026-06-25 10:47:28,33.65,221065216,0.68,0,0
    2026-06-25 10:47:29,36.66,221114368,0.68,0,0
    2026-06-25 10:47:30,39.54,221155328,0.68,0,0
    2026-06-25 10:47:31,34.71,221212672,0.68,0,4096
    2026-06-25 10:47:32,39.60,221261824,0.68,0,0
    2026-06-25 10:47:33,36.71,221278208,0.68,0,0
    2026-06-25 10:47:34,38.68,221278208,0.68,0,0
    2026-06-25 10:47:35,35.61,221306880,0.68,0,0
    2026-06-25 10:47:36,39.67,221331456,0.68,0,0
    2026-06-25 10:47:38,36.66,221347840,0.68,0,4096
    2026-06-25 10:47:39,41.60,221351936,0.68,0,0
    2026-06-25 10:47:40,38.65,221356032,0.68,0,0
    2026-06-25 10:47:41,41.60,221356032,0.68,0,0
    2026-06-25 10:47:42,39.59,221356032,0.68,0,0
    2026-06-25 10:47:43,0.00,221356032,0.68,0,0
    2026-06-25 10:47:44,0.00,221356032,0.68,0,0
    2026-06-25 10:47:45,0.00,221356032,0.68,0,0
    2026-06-25 10:47:46,0.00,221356032,0.68,0,0
    2026-06-25 10:47:47,1.97,221356032,0.68,0,0

    Means: 26.00,39.51,221356032.00,0.65,798720.00,11849728.00


    geth
    timestamp,cpu_pct,mem_rss_bytes,mem_pct,disk_read_bytes,disk_write_bytes
    2026-06-26 10:50:16,0.00,11173888,0.03,0,16384
    2026-06-26 10:50:17,192.24,191000576,0.58,0,348160
    2026-06-26 10:50:18,8.93,201220096,0.61,0,11472896
    2026-06-26 10:50:19,45.62,222150656,0.68,0,0
    2026-06-26 10:50:20,38.69,222216192,0.68,0,4096
    2026-06-26 10:50:21,40.61,222306304,0.68,0,0
    2026-06-26 10:50:22,38.69,222388224,0.68,0,0
    2026-06-26 10:50:23,34.78,222425088,0.68,0,0
    2026-06-26 10:50:24,39.72,222482432,0.68,0,0
    2026-06-26 10:50:25,34.91,222494720,0.68,0,0
    2026-06-26 10:50:26,38.74,222543872,0.68,0,4096
    2026-06-26 10:50:27,32.74,222572544,0.68,0,0
    2026-06-26 10:50:28,40.64,222625792,0.68,0,0
    2026-06-26 10:50:29,40.68,222633984,0.68,0,0
    2026-06-26 10:50:30,34.68,222642176,0.68,0,0
    2026-06-26 10:50:31,37.61,222642176,0.68,0,0
    2026-06-26 10:50:32,36.75,222674944,0.68,0,0
    2026-06-26 10:50:34,36.68,222679040,0.68,0,4096
    2026-06-26 10:50:35,40.58,222683136,0.68,0,0
    2026-06-26 10:50:36,40.71,222703616,0.68,0,0
    2026-06-26 10:50:37,40.71,222703616,0.68,0,0
    2026-06-26 10:50:38,38.79,222703616,0.68,0,0
    2026-06-26 10:50:39,0.00,222703616,0.68,0,0
    2026-06-26 10:50:40,0.00,222703616,0.68,0,0
    2026-06-26 10:50:41,0.00,222703616,0.68,0,0
    2026-06-26 10:50:42,0.00,222703616,0.68,0,0
    2026-06-26 10:50:43,2.97,222703616,0.68,0,0

    Means: 27.00,34.68,222703616.00,0.65,0.00,11849728.00
    """
    folder = orchestrator._get_directories_from_folder('./tests/fake_folder/')
    networks = ['geth', 'anvil']
    conditional_funct = fake_conditional_function

    total_metrics = orchestrator._get_concat_metrics_by_network(folder, networks, conditional_funct)

    assert total_metrics['anvil']['timestamp'].mean().round(2) == 26
    assert total_metrics['anvil']['cpu_pct'].mean().round(2) == 39.51
    assert total_metrics['anvil']['mem_rss_bytes'].mean().round(2) == 221356032.00
    assert total_metrics['anvil']['mem_pct'].mean().round(2) == 0.65
    assert total_metrics['anvil']['disk_read_bytes'].mean().round(2) == 798720.00
    assert total_metrics['anvil']['disk_write_bytes'].mean().round(2) == 11849728.00

    assert total_metrics['geth']['timestamp'].mean().round(2) == 27
    assert total_metrics['geth']['cpu_pct'].mean().round(2) == 34.68
    assert total_metrics['geth']['mem_rss_bytes'].mean().round(2) == 222703616.00
    assert total_metrics['geth']['mem_pct'].mean().round(2) == 0.65
    assert total_metrics['geth']['disk_read_bytes'].mean().round(2) == 0.00
    assert total_metrics['geth']['disk_write_bytes'].mean().round(2) == 11849728.00


def test_get_concat_metrics_by_network_when_hardhat_network_contains_valid_rosbags_metrics():
    """
    timestamp,cpu_pct,mem_rss_bytes,mem_pct,disk_read_bytes,disk_write_bytes
    2026-06-26 10:44:50,0.00,11124736,0.03,0,16384
    2026-06-26 10:44:51,191.25,191193088,0.58,0,348160
    2026-06-26 10:44:52,14.88,206589952,0.63,0,11472896
    2026-06-26 10:44:53,70.53,222556160,0.68,0,4096
    2026-06-26 10:44:54,68.74,222699520,0.68,0,0
    2026-06-26 10:44:55,67.55,222781440,0.68,0,0
    2026-06-26 10:44:56,68.54,222863360,0.68,0,0
    2026-06-26 10:44:57,66.56,222916608,0.68,0,4096
    2026-06-26 10:44:58,66.58,222978048,0.68,0,0
    2026-06-26 10:44:59,67.61,222994432,0.68,0,0
    2026-06-26 10:45:00,65.48,223010816,0.68,0,4096
    2026-06-26 10:45:01,67.55,223031296,0.68,0,0
    2026-06-26 10:45:02,68.51,223051776,0.68,0,0
    2026-06-26 10:45:03,38.71,223051776,0.68,0,0
    2026-06-26 10:45:04,0.00,223051776,0.68,0,0
    2026-06-26 10:45:05,0.00,223051776,0.68,0,0
    2026-06-26 10:45:06,0.00,223051776,0.68,0,0
    2026-06-26 10:45:07,0.00,223051776,0.68,0,0

    Means: 17.00,51.25,223051776.00,0.64,0.00,11849728.00

    timestamp,cpu_pct,mem_rss_bytes,mem_pct,disk_read_bytes,disk_write_bytes
    2026-06-26 10:44:19,0.00,11399168,0.03,4096,16384
    2026-06-26 10:44:20,192.99,188137472,0.57,26648576,348160
    2026-06-26 10:44:21,6.95,188321792,0.58,0,11354112
    2026-06-26 10:44:22,61.51,218370048,0.67,8474624,122880
    2026-06-26 10:44:23,68.66,218513408,0.67,0,0
    2026-06-26 10:44:24,66.69,218574848,0.67,0,0
    2026-06-26 10:44:25,66.58,218677248,0.67,0,0
    2026-06-26 10:44:26,66.47,218767360,0.67,0,8192
    2026-06-26 10:44:27,67.47,218800128,0.67,0,0
    2026-06-26 10:44:28,66.67,218816512,0.67,0,0
    2026-06-26 10:44:29,65.54,218841088,0.67,0,4096
    2026-06-26 10:44:30,66.50,218886144,0.67,0,0
    2026-06-26 10:44:31,66.69,218906624,0.67,0,0
    2026-06-26 10:44:32,64.62,218906624,0.67,0,0
    2026-06-26 10:44:33,12.88,218906624,0.67,0,0
    2026-06-26 10:44:34,0.00,218906624,0.67,0,0
    2026-06-26 10:44:35,0.00,218906624,0.67,0,0
    2026-06-26 10:44:36,0.00,218906624,0.67,0,0
    2026-06-26 10:44:37,0.00,218906624,0.67,0,0

    Means: 18.00,49.49,218906624.00,0.63,35127296.00,11853824.00

    Total means: 17.50,50.34,220979200.00,0.63,17563648.00,11851776.00
    """
    folder = orchestrator._get_directories_from_folder('./tests/fake_folder/')
    networks = ['hardhat']
    conditional_funct = fake_conditional_function

    total_metrics = orchestrator._get_concat_metrics_by_network(folder, networks, conditional_funct)

    assert total_metrics['hardhat']['timestamp'].mean().round(2) == 17.5
    assert total_metrics['hardhat']['cpu_pct'].mean().round(2) == 50.34
    assert total_metrics['hardhat']['mem_rss_bytes'].mean().round(2) == 220979200.00
    assert total_metrics['hardhat']['mem_pct'].mean().round(2) == 0.63
    assert total_metrics['hardhat']['disk_read_bytes'].mean().round(2) == 17563648.00
    assert total_metrics['hardhat']['disk_write_bytes'].mean().round(2) == 11851776.00

@pytest.mark.usefixtures("cleanup_files")
def test_build_csv_when_anvil_network_contains_valid_rosbag_metrics():
    """
    timestamp,cpu_pct,mem_rss_bytes,mem_pct,disk_read_bytes,disk_write_bytes
    2026-06-25 10:47:21,120.00,11124736,0.03,0,16384
    2026-06-25 10:47:22,192.16,191463424,0.58,704512,348160
    2026-06-25 10:47:23,18.84,202129408,0.62,94208,11472896
    2026-06-25 10:47:24,42.57,220807168,0.67,0,0
    2026-06-25 10:47:25,42.61,220880896,0.67,0,4096
    2026-06-25 10:47:26,34.64,220983296,0.67,0,0
    2026-06-25 10:47:27,41.62,221048832,0.68,0,0
    2026-06-25 10:47:28,33.65,221065216,0.68,0,0
    2026-06-25 10:47:29,36.66,221114368,0.68,0,0
    2026-06-25 10:47:30,39.54,221155328,0.68,0,0
    2026-06-25 10:47:31,34.71,221212672,0.68,0,4096
    2026-06-25 10:47:32,39.60,221261824,0.68,0,0
    2026-06-25 10:47:33,36.71,221278208,0.68,0,0
    2026-06-25 10:47:34,38.68,221278208,0.68,0,0
    2026-06-25 10:47:35,35.61,221306880,0.68,0,0
    2026-06-25 10:47:36,39.67,221331456,0.68,0,0
    2026-06-25 10:47:38,36.66,221347840,0.68,0,4096
    2026-06-25 10:47:39,41.60,221351936,0.68,0,0
    2026-06-25 10:47:40,38.65,221356032,0.68,0,0
    2026-06-25 10:47:41,41.60,221356032,0.68,0,0
    2026-06-25 10:47:42,39.59,221356032,0.68,0,0
    2026-06-25 10:47:43,0.00,221356032,0.68,0,0
    2026-06-25 10:47:44,0.00,221356032,0.68,0,0
    2026-06-25 10:47:45,0.00,221356032,0.68,0,0
    2026-06-25 10:47:46,0.00,221356032,0.68,0,0
    2026-06-25 10:47:47,1.97,221356032,0.68,0,0

    Means: 26.00,39.51,221356032.00,0.65,798720.00,11849728.00
    """
    folder = orchestrator._get_directories_from_folder('./tests/fake_folder/')
    networks = ['anvil']
    conditional_funct = fake_conditional_function

    total_metrics = orchestrator._get_concat_metrics_by_network(folder, networks, conditional_funct)
    orchestrator._build_csv(FAKE_CSV_FILE, total_metrics)

    fake_csv = pandas.read_csv(FAKE_CSV_FILE, index_col=False)

    assert fake_csv['network'].item() == 'anvil'
    assert fake_csv['time'].item() == 26.0
    assert fake_csv['cpu_pct_min'].item() == 0.0
    assert fake_csv['cpu_pct_max'].item() == 192.16
    assert fake_csv['cpu_pct_mean'].item() == 39.513
    assert fake_csv['mem_rss_bytes_mean'].item() == 221356032.00
    assert fake_csv['mem_pct_min'].item() == 0.03
    assert fake_csv['mem_pct_max'].item() == 0.68
    assert fake_csv['mem_pct_mean'].item() == 0.648
    assert fake_csv['disk_read_bytes_mean'].item() == 798720.00
    assert fake_csv['disk_write_bytes_mean'].item() == 11849728.00


@pytest.mark.usefixtures("cleanup_files")
def test_build_csv_when_geth_network_contains_valid_rosbag_metrics():
    """
    timestamp,cpu_pct,mem_rss_bytes,mem_pct,disk_read_bytes,disk_write_bytes
    2026-06-26 10:50:16,0.00,11173888,0.03,0,16384
    2026-06-26 10:50:17,192.24,191000576,0.58,0,348160
    2026-06-26 10:50:18,8.93,201220096,0.61,0,11472896
    2026-06-26 10:50:19,45.62,222150656,0.68,0,0
    2026-06-26 10:50:20,38.69,222216192,0.68,0,4096
    2026-06-26 10:50:21,40.61,222306304,0.68,0,0
    2026-06-26 10:50:22,38.69,222388224,0.68,0,0
    2026-06-26 10:50:23,34.78,222425088,0.68,0,0
    2026-06-26 10:50:24,39.72,222482432,0.68,0,0
    2026-06-26 10:50:25,34.91,222494720,0.68,0,0
    2026-06-26 10:50:26,38.74,222543872,0.68,0,4096
    2026-06-26 10:50:27,32.74,222572544,0.68,0,0
    2026-06-26 10:50:28,40.64,222625792,0.68,0,0
    2026-06-26 10:50:29,40.68,222633984,0.68,0,0
    2026-06-26 10:50:30,34.68,222642176,0.68,0,0
    2026-06-26 10:50:31,37.61,222642176,0.68,0,0
    2026-06-26 10:50:32,36.75,222674944,0.68,0,0
    2026-06-26 10:50:34,36.68,222679040,0.68,0,4096
    2026-06-26 10:50:35,40.58,222683136,0.68,0,0
    2026-06-26 10:50:36,40.71,222703616,0.68,0,0
    2026-06-26 10:50:37,40.71,222703616,0.68,0,0
    2026-06-26 10:50:38,38.79,222703616,0.68,0,0
    2026-06-26 10:50:39,0.00,222703616,0.68,0,0
    2026-06-26 10:50:40,0.00,222703616,0.68,0,0
    2026-06-26 10:50:41,0.00,222703616,0.68,0,0
    2026-06-26 10:50:42,0.00,222703616,0.68,0,0
    2026-06-26 10:50:43,2.97,222703616,0.68,0,0

    Means: 27.00,34.68,222703616.00,0.65,0.00,11849728.00
    """
    folder = orchestrator._get_directories_from_folder('./tests/fake_folder/')
    networks = ['geth']
    conditional_funct = fake_conditional_function

    total_metrics = orchestrator._get_concat_metrics_by_network(folder, networks, conditional_funct)
    orchestrator._build_csv(FAKE_CSV_FILE, total_metrics)

    fake_csv = pandas.read_csv(FAKE_CSV_FILE, index_col=False)

    assert fake_csv['network'].item() == 'geth'
    assert fake_csv['time'].item() == 27.0
    assert fake_csv['cpu_pct_min'].item() == 0.0
    assert fake_csv['cpu_pct_max'].item() == 192.24
    assert fake_csv['cpu_pct_mean'].item() == 34.684
    assert fake_csv['mem_rss_bytes_mean'].item() == 222703616.00
    assert fake_csv['mem_pct_min'].item() == 0.03
    assert fake_csv['mem_pct_max'].item() == 0.68
    assert fake_csv['mem_pct_mean'].item() == 0.65
    assert fake_csv['disk_read_bytes_mean'].item() == 0.00
    assert fake_csv['disk_write_bytes_mean'].item() == 11849728.00


@pytest.mark.usefixtures("cleanup_files")
def test_build_csv_when_anvil_and_geth_networks_contains_valid_rosbag_metrics():
    """
    anvil
    timestamp,cpu_pct,mem_rss_bytes,mem_pct,disk_read_bytes,disk_write_bytes
    2026-06-25 10:47:21,120.00,11124736,0.03,0,16384
    2026-06-25 10:47:22,192.16,191463424,0.58,704512,348160
    2026-06-25 10:47:23,18.84,202129408,0.62,94208,11472896
    2026-06-25 10:47:24,42.57,220807168,0.67,0,0
    2026-06-25 10:47:25,42.61,220880896,0.67,0,4096
    2026-06-25 10:47:26,34.64,220983296,0.67,0,0
    2026-06-25 10:47:27,41.62,221048832,0.68,0,0
    2026-06-25 10:47:28,33.65,221065216,0.68,0,0
    2026-06-25 10:47:29,36.66,221114368,0.68,0,0
    2026-06-25 10:47:30,39.54,221155328,0.68,0,0
    2026-06-25 10:47:31,34.71,221212672,0.68,0,4096
    2026-06-25 10:47:32,39.60,221261824,0.68,0,0
    2026-06-25 10:47:33,36.71,221278208,0.68,0,0
    2026-06-25 10:47:34,38.68,221278208,0.68,0,0
    2026-06-25 10:47:35,35.61,221306880,0.68,0,0
    2026-06-25 10:47:36,39.67,221331456,0.68,0,0
    2026-06-25 10:47:38,36.66,221347840,0.68,0,4096
    2026-06-25 10:47:39,41.60,221351936,0.68,0,0
    2026-06-25 10:47:40,38.65,221356032,0.68,0,0
    2026-06-25 10:47:41,41.60,221356032,0.68,0,0
    2026-06-25 10:47:42,39.59,221356032,0.68,0,0
    2026-06-25 10:47:43,0.00,221356032,0.68,0,0
    2026-06-25 10:47:44,0.00,221356032,0.68,0,0
    2026-06-25 10:47:45,0.00,221356032,0.68,0,0
    2026-06-25 10:47:46,0.00,221356032,0.68,0,0
    2026-06-25 10:47:47,1.97,221356032,0.68,0,0

    Means: 26.00,39.51,221356032.00,0.65,798720.00,11849728.00


    geth
    timestamp,cpu_pct,mem_rss_bytes,mem_pct,disk_read_bytes,disk_write_bytes
    2026-06-26 10:50:16,0.00,11173888,0.03,0,16384
    2026-06-26 10:50:17,192.24,191000576,0.58,0,348160
    2026-06-26 10:50:18,8.93,201220096,0.61,0,11472896
    2026-06-26 10:50:19,45.62,222150656,0.68,0,0
    2026-06-26 10:50:20,38.69,222216192,0.68,0,4096
    2026-06-26 10:50:21,40.61,222306304,0.68,0,0
    2026-06-26 10:50:22,38.69,222388224,0.68,0,0
    2026-06-26 10:50:23,34.78,222425088,0.68,0,0
    2026-06-26 10:50:24,39.72,222482432,0.68,0,0
    2026-06-26 10:50:25,34.91,222494720,0.68,0,0
    2026-06-26 10:50:26,38.74,222543872,0.68,0,4096
    2026-06-26 10:50:27,32.74,222572544,0.68,0,0
    2026-06-26 10:50:28,40.64,222625792,0.68,0,0
    2026-06-26 10:50:29,40.68,222633984,0.68,0,0
    2026-06-26 10:50:30,34.68,222642176,0.68,0,0
    2026-06-26 10:50:31,37.61,222642176,0.68,0,0
    2026-06-26 10:50:32,36.75,222674944,0.68,0,0
    2026-06-26 10:50:34,36.68,222679040,0.68,0,4096
    2026-06-26 10:50:35,40.58,222683136,0.68,0,0
    2026-06-26 10:50:36,40.71,222703616,0.68,0,0
    2026-06-26 10:50:37,40.71,222703616,0.68,0,0
    2026-06-26 10:50:38,38.79,222703616,0.68,0,0
    2026-06-26 10:50:39,0.00,222703616,0.68,0,0
    2026-06-26 10:50:40,0.00,222703616,0.68,0,0
    2026-06-26 10:50:41,0.00,222703616,0.68,0,0
    2026-06-26 10:50:42,0.00,222703616,0.68,0,0
    2026-06-26 10:50:43,2.97,222703616,0.68,0,0

    Means: 27.00,34.68,222703616.00,0.65,0.00,11849728.00
    """
    folder = orchestrator._get_directories_from_folder('./tests/fake_folder/')
    networks = ['geth', 'anvil']
    conditional_funct = fake_conditional_function

    total_metrics = orchestrator._get_concat_metrics_by_network(folder, networks, conditional_funct)
    orchestrator._build_csv(FAKE_CSV_FILE, total_metrics)

    fake_csv = pandas.read_csv(FAKE_CSV_FILE, index_col=False)

    assert fake_csv['network'][0] == 'geth'
    assert fake_csv['time'][0]  == 27.0
    assert fake_csv['cpu_pct_min'][0]  == 0.0
    assert fake_csv['cpu_pct_max'][0]  == 192.24
    assert fake_csv['cpu_pct_mean'][0]  == 34.684
    assert fake_csv['mem_rss_bytes_mean'][0]  == 222703616.00
    assert fake_csv['mem_pct_min'][0]  == 0.03
    assert fake_csv['mem_pct_max'][0]  == 0.68
    assert fake_csv['mem_pct_mean'][0]  == 0.65
    assert fake_csv['disk_read_bytes_mean'][0]  == 0.00
    assert fake_csv['disk_write_bytes_mean'][0]  == 11849728.00

    assert fake_csv['network'][1] == 'anvil'
    assert fake_csv['time'][1] == 26.0
    assert fake_csv['cpu_pct_min'][1] == 0.0
    assert fake_csv['cpu_pct_max'][1] == 192.16
    assert fake_csv['cpu_pct_mean'][1] == 39.513
    assert fake_csv['mem_rss_bytes_mean'][1] == 221356032.00
    assert fake_csv['mem_pct_min'][1] == 0.03
    assert fake_csv['mem_pct_max'][1] == 0.68
    assert fake_csv['mem_pct_mean'][1] == 0.648
    assert fake_csv['disk_read_bytes_mean'][1] == 798720.00
    assert fake_csv['disk_write_bytes_mean'][1] == 11849728.00


@pytest.mark.usefixtures("cleanup_files")
def test_build_csv_when_hardhat_network_contains_valid_rosbags_metrics():
    """
    timestamp,cpu_pct,mem_rss_bytes,mem_pct,disk_read_bytes,disk_write_bytes
    2026-06-26 10:44:50,0.00,11124736,0.03,0,16384
    2026-06-26 10:44:51,191.25,191193088,0.58,0,348160
    2026-06-26 10:44:52,14.88,206589952,0.63,0,11472896
    2026-06-26 10:44:53,70.53,222556160,0.68,0,4096
    2026-06-26 10:44:54,68.74,222699520,0.68,0,0
    2026-06-26 10:44:55,67.55,222781440,0.68,0,0
    2026-06-26 10:44:56,68.54,222863360,0.68,0,0
    2026-06-26 10:44:57,66.56,222916608,0.68,0,4096
    2026-06-26 10:44:58,66.58,222978048,0.68,0,0
    2026-06-26 10:44:59,67.61,222994432,0.68,0,0
    2026-06-26 10:45:00,65.48,223010816,0.68,0,4096
    2026-06-26 10:45:01,67.55,223031296,0.68,0,0
    2026-06-26 10:45:02,68.51,223051776,0.68,0,0
    2026-06-26 10:45:03,38.71,223051776,0.68,0,0
    2026-06-26 10:45:04,0.00,223051776,0.68,0,0
    2026-06-26 10:45:05,0.00,223051776,0.68,0,0
    2026-06-26 10:45:06,0.00,223051776,0.68,0,0
    2026-06-26 10:45:07,0.00,223051776,0.68,0,0

    Means: 17.00,51.25,223051776.00,0.64,0.00,11849728.00

    timestamp,cpu_pct,mem_rss_bytes,mem_pct,disk_read_bytes,disk_write_bytes
    2026-06-26 10:44:19,0.00,11399168,0.03,4096,16384
    2026-06-26 10:44:20,192.99,188137472,0.57,26648576,348160
    2026-06-26 10:44:21,6.95,188321792,0.58,0,11354112
    2026-06-26 10:44:22,61.51,218370048,0.67,8474624,122880
    2026-06-26 10:44:23,68.66,218513408,0.67,0,0
    2026-06-26 10:44:24,66.69,218574848,0.67,0,0
    2026-06-26 10:44:25,66.58,218677248,0.67,0,0
    2026-06-26 10:44:26,66.47,218767360,0.67,0,8192
    2026-06-26 10:44:27,67.47,218800128,0.67,0,0
    2026-06-26 10:44:28,66.67,218816512,0.67,0,0
    2026-06-26 10:44:29,65.54,218841088,0.67,0,4096
    2026-06-26 10:44:30,66.50,218886144,0.67,0,0
    2026-06-26 10:44:31,66.69,218906624,0.67,0,0
    2026-06-26 10:44:32,64.62,218906624,0.67,0,0
    2026-06-26 10:44:33,12.88,218906624,0.67,0,0
    2026-06-26 10:44:34,0.00,218906624,0.67,0,0
    2026-06-26 10:44:35,0.00,218906624,0.67,0,0
    2026-06-26 10:44:36,0.00,218906624,0.67,0,0
    2026-06-26 10:44:37,0.00,218906624,0.67,0,0

    Means: 18.00,49.49,218906624.00,0.63,35127296.00,11853824.00

    Total means: 17.50,50.34,220979200.00,0.63,17563648.00,11851776.00
    """
    folder = orchestrator._get_directories_from_folder('./tests/fake_folder/')
    networks = ['hardhat']
    conditional_funct = fake_conditional_function

    total_metrics = orchestrator._get_concat_metrics_by_network(folder, networks, conditional_funct)
    orchestrator._build_csv(FAKE_CSV_FILE, total_metrics)

    fake_csv = pandas.read_csv(FAKE_CSV_FILE, index_col=False)

    assert fake_csv['network'].item() == 'hardhat'
    assert fake_csv['time'].item() == 17.5
    assert fake_csv['cpu_pct_min'].item() == 0.0
    assert fake_csv['cpu_pct_max'].item() == 192.99
    assert fake_csv['cpu_pct_mean'].item() == 50.344
    assert fake_csv['mem_rss_bytes_mean'].item() == 220979200.00
    assert fake_csv['mem_pct_min'].item() == 0.03
    assert fake_csv['mem_pct_max'].item() == 0.68
    assert fake_csv['mem_pct_mean'].item() == 0.631
    assert fake_csv['disk_read_bytes_mean'].item() == 17563648.00
    assert fake_csv['disk_write_bytes_mean'].item() == 11851776.00
