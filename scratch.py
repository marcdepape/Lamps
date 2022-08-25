for i in range(number_of_lamps):
    tries = 0
    duplicate = -1
    assignment = 0
    if new_states[i] == default:
        while new_states[i] == default:
            assignment = random.choice(broadcast_lamps)
            if assignment != old[i]:
                new_states[i] = assignment
                broadcast_lamps.remove(assignment)
                stream_count[i] = stream_count[i] + 1
                broadcast_count[i] = 0
            else:
                print("ALREADY STREAMING {}".format(assignment))
                tries = tries + 1

        if tries >= number_of_lamps:
            swaping = True
            while swaping:
                swap = random.randint(0, number_of_lamps-1)
                if swap != i and new_states[swap] != broadcast:
                    print("SWAPING {} and {}".format(i, swap))
                    new_stream = new_states[swap]
                    new_states[swap] = assignment
                    new_states[i] = new_stream
                    swaping = False
