FROM python:3.9.5

COPY . .

RUN python3.9 build.py build_ext --inplace
RUN mv mapanalyzerext.*.so mapanalyzerext.so

CMD ["/bin/bash"]
