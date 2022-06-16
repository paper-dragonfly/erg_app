from erg_app import erg_front as front

def test_duration_to_seconds():
    secs = front.duration_to_seconds('00:01:40.00')
    assert secs == 100
 
# def test_front():
#     input_values = [2, 3]
#     output = []
 
#     def mock_input(s):
#         output.append(s)
#         return input_values.pop(0)
#     front.input = mock_input
#     front.print = lambda s : output.append(s)
 
#     front.main()
 
#     assert output == [
#         'First: ',
#         'Second: ', 
#         'The result is 5',
#     ]
 