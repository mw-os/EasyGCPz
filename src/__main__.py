from easygcpz import EasyGCPz

if __name__ == '__main__':
    print(f'running {pathlib.Path(__file__).as_posix()} directly')

    with EasyGCPz(sys.argv[0], sys.argv[1], verbose=True) as tmp:
        if len(sys.argv) <= 7:
            tmp.query(queries=sys.argv[2],
                      return_format=sys.argv[3] if
                      len(sys.argv) >= 4 else 'dict',
                      return_ascii=bool(sys.argv[4]) if
                      len(sys.argv) >= 5 else True,
                      file_separate=sys.argv[5] if
                      len(sys.argv) >= 6 else '',
                      file_same=sys.argv[6] if
                      len(sys.argv) >= 7 else '')
        else:
            # build incoming kwargs dict from every other element
            # being a key and value pair
            kwargs_l = sys.argv[7:]
            kwargs_k = [i for i in kwargs_l if i % 2 == 0]
            kwargs_v = [i for i in kwargs_l if i % 2 == 1]
            dict_ = {kwargs_k[i]: kwargs_v[i] for i in range(len(kwargs_k))}
            tmp.query(queries=sys.argv[2],
                      return_format=sys.argv[3],
                      return_ascii=bool(sys.argv[4]),
                      file_separate=sys.argv[5],
                      file_same=sys.argv[6],
                      **dict_)

# eof
