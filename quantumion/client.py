import socket
import pathlib
import h5py
import time
import select
import io


class Backend:
    def __init__(self, server: str = '0.0.0.0', port: int = 1234):
        self.server = server
        self.port = port
        return

    def submit_job(self, file, filename):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
                client.connect((self.server, self.port))
                client.send(f"queue|{filename}".encode('utf-8'))
                response = client.recv(1024)

                client.send(file.encode('utf-8'))
                job_id = client.recv(1024).decode("utf-8")
                return job_id

        except Exception as e:
            print(f"Error: {e}")

    def get_results(self, job_id):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
                client.connect((self.server, self.port))
                client.send(f"result|{job_id}".encode('utf-8'))

                data = b''
                while True:
                    available = select.select([client], [], [], 1.0)  # timeout of 1.0 seconds
                    if available[0]:
                        bytes_read = client.recv(1024)
                        data += bytes_read
                    else:
                        break

                f = io.BytesIO(data)
                data = h5py.File(f, 'r')
            return data

        except Exception as e:
            print(f"Error: {e}")

    def get_status(self, job_id):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect((self.server, self.port))
            client.send(f"status|{job_id}".encode('utf-8'))
            status = client.recv(1024).decode('utf-8')
        return status


if __name__ == "__main__":

    # path = pathlib.Path(r'/Users/benjamin/Library/CloudStorage/OneDrive-UniversityofWaterloo/Desktop/1 - Projects/Open Quantum Designs/quantumion/qasm_example.qasm')
    # with path.open() as file:
    #     file_data = file.read()

    filename = "test_qasm.qasm"
    file = """
    include "qelib1.inc";
    qreg q[2];
    
    h q[0];
    cx q[0],q[1];
    """

    client = Backend(server='0.0.0.0')
    job_id = client.submit_job(filename='test.qasm', file=file)

    while client.get_status(job_id) != "finished":
        time.sleep(0.2)

    status = client.get_status(job_id)
    print(f"Job {job_id} | Status: {status}")

    data = client.get_results(job_id)
    print(f"Data keys: {data.keys()}")

