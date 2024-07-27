import tkinter as tk
import math


def validate_number(value_if_allowed, text):
    """
    Validates if the input is a non-negative integer.
    Parameters:
    - value_if_allowed: str, the current value of the input field.
    - text: str, the new text being inserted or deleted.

    Returns:
    - bool: True if the input is valid (empty or a non-negative integer), False otherwise.
    """
    if value_if_allowed == "":
        return True  # Allow empty string (i.e., cleared input field)
    try:
        int_value = int(value_if_allowed)  # Try to convert to integer
        return int_value >= 0  # Only allow non-negative integers
    except ValueError:
        return False  # Reject any non-integer input


def getCost(curr, lvl, mvp, options):
    """
    Calculates the cost of enhancing an item based on the current star level.
    Parameters:
    - curr: int, current star level.
    - lvl: int, item level.
    - discount: float, discount factor.
    - options: list, boolean values for various enhancement options.

    Returns:
    - cost: float, the calculated cost.
    """
    if curr < 10:
        # For star levels 0-9
        cost = 100 * round((lvl ** 3) * (curr + 1) / 2500 + 10)
    elif curr < 15:
        # For star levels 10-14
        divisors = (40000, 22000, 15000, 11000, 7500)
        cost = 100 * round((lvl ** 3) * (curr + 1) ** 2.7 / divisors[curr - 10] + 10)
    else:
        # For star levels 15+
        cost = 100 * round((lvl ** 3) * (curr + 1) ** 2.7 / 20000 + 10)

    discount = 1

    # Check for 30% off
    if options[2]:
        discount -= .3

    # Apply mvp discount
    if curr <= 15:
        discount -= mvp

    # Apply safeguard cost doubling for stars 15 and 16 if safeguard is used
    if options[4] and curr in (15, 16):
        if not (options[0] and curr == 15):  # Don't double cost if 100% success is used for star 15
            discount += 1

    cost *= discount

    return cost


def getSuccess(curr, odds, options):
    """
    Retrieves the success, maintain, decrease, and boom probabilities for enhancing an item.
    Parameters:
    - curr: int, current star level.
    - odds: tuple of lists, base success rates and other probabilities.
    - options: list, boolean values for various enhancement options.

    Returns:
    - tuple: success, maintain, decrease, boom probabilities.
    """
    # Apply Star Catching option to success rate
    success = odds[0][curr] * 1.05 if options[3] else odds[0][curr]
    total_fail_rate = 1 - success  # Total failure rate (1 - success rate)
    maintain = total_fail_rate * odds[1][curr]  # Probability of maintaining the current star level
    decrease = total_fail_rate * odds[2][curr]  # Probability of decreasing the star level
    boom = total_fail_rate * odds[3][curr]  # Probability of destroying the item (boom)

    if options[4] and curr in (15, 16):
        # For stars 15 and 16, if safeguard is used
        maintain = decrease = maintain + decrease + boom
        boom = 0  # Safeguard prevents booming

    if options[0] and curr in (5, 10, 15):
        # If 100% success option is selected for stars 5, 10, and 15
        success, maintain, decrease, boom = 1, 0, 0, 0  # Guarantee success

    return success, maintain, decrease, boom


def calculate_stars(entry1, entry2, entry3, result_label, checkboxes, mvp_discount):
    """
    Calculates the expected cost to reach a target star level from a current star level.
    Parameters:
    - entry1: tk.Entry, item level input.
    - entry2: tk.Entry, current star level input.
    - entry3: tk.Entry, target star level input.
    - result_label: tk.Label, label to display the result.
    - checkboxes: list, boolean values for various enhancement options.
    - mvp_discount: str, MVP discount option selected.

    Updates:
    - result_label: with the calculated expected cost.
    """
    entries = [entry1, entry2, entry3]
    labels = ["Item Level", "Current Star", "Target Star"]

    # Validate input fields
    for entry, label in zip(entries, labels):
        if entry.get() == "":
            result_label.config(text="Invalid input")  # Display error if any input is empty
            return

    # Parse input values
    itemLevel = int(entry1.get())
    StartStar = int(entry2.get())
    TargetStar = int(entry3.get())
    currentStar = StartStar if StartStar <= 12 else 12  # Set initial star level (cap at 12 for initial calculation)
    checkbox_values = [var.get() for var in checkboxes]  # Get checkbox states

    if TargetStar < StartStar or TargetStar > 25:
        result_label.config(text="Invalid TargetStar")  # Display error if target star is invalid
        return

    total = [0] * 26  # Initialize total costs array
    noBoomProbs = [1] * 26  # Keeps track of the probability not to boom at each step for distribution later
    expectedBooms = [0] * 26  # Keeps track of the expected boom probabilities at each step to be summed

    # Base probabilities for success, maintain, decrease, and boom rates
    baseOdds = (
        (.95, .9, .85, .85, .8, .75, .7, .65, .6, .55, .5, .45, .4, .35, .3, .3, .3, .3, .3, .3, .3, .3, .03, .02, .01),
        (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, .97, 0, 0, 0, 0, .9, 0, 0, 0, 0),
        (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, .97, .97, .96, .96, 0, .9, .8, .7, .6),
        (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, .03, .03, .03, .04, .04, .1, .1, .2, .3, .4)
    )

    # Initialize variables for tracking costs
    lastFailDecrease, lastFailDestroy, twoCostAgo, lastCost = (0,) * 4

    # Determine MVP discount rate
    if mvp_discount == "MVP silver (3% off 1 to 16)":
        mvp = 0.03
    elif mvp_discount == "MVP gold (5% off 1 to 16)":
        mvp = 0.05
    elif mvp_discount == "MVP Diamond (10% off 1 to 16)":
        mvp = 0.1
    else:
        mvp = 0

    # Calculate total cost to reach target star
    while currentStar < TargetStar:
        # Set probabilities of each outcome and get the base cost
        success_rate, fail_maintain, fail_decrease, fail_destroy = getSuccess(currentStar, baseOdds, checkbox_values)
        cost = getCost(currentStar, itemLevel, mvp, checkbox_values)

        # Start the calculation for each star based on the current star
        if currentStar < 15:
            total[currentStar + 1] = cost / success_rate

        elif currentStar == 15 or currentStar == 20:
            total[currentStar + 1] = (cost + fail_destroy * sum(total[13:currentStar + 1])) / success_rate
            noBoomProbs[currentStar + 1] = success_rate / (success_rate + fail_destroy)
            expectedBooms[currentStar + 1] = (fail_destroy * (1 + sum(expectedBooms[16:currentStar + 1]))) / success_rate

            # Adjust the previous rates
            lastFailDecrease, lastFailDestroy, twoCostAgo, lastCost = fail_decrease, fail_destroy, lastCost, cost

        elif currentStar == 16 or currentStar == 21:
            total[currentStar + 1] = (cost + fail_decrease * total[currentStar] + fail_destroy *
                                      sum(total[13:currentStar + 1])) / success_rate
            noBoomProbs[currentStar + 1] = success_rate / (success_rate + fail_destroy + fail_decrease * (1 - noBoomProbs[currentStar]))
            expectedBooms[currentStar + 1] = (fail_destroy * (1 + sum(expectedBooms[16:currentStar + 1])) +
                                              fail_decrease * expectedBooms[currentStar]) / success_rate

            # Adjust the previous rates and two ago
            lastFailDecrease, lastFailDestroy, twoCostAgo, lastCost = fail_decrease, fail_destroy, lastCost, cost

        else:
            total[currentStar + 1] = (cost +
                                      fail_decrease * lastCost +
                                      fail_decrease * lastFailDecrease * (twoCostAgo + total[currentStar]) +
                                      (fail_decrease * lastFailDestroy + fail_destroy) * sum(total[13:currentStar + 1])
                                      ) / success_rate
            noBoomProbs[currentStar + 1] = success_rate / (success_rate +
                                                           fail_destroy +
                                                           fail_decrease * lastFailDecrease * (1 - noBoomProbs[currentStar]) +
                                                           fail_decrease * lastFailDestroy)
            expectedBooms[currentStar + 1] = (fail_decrease * lastFailDecrease * expectedBooms[currentStar] +
                                              (sum(expectedBooms[16:currentStar + 1]) + 1) * (fail_decrease * lastFailDestroy + fail_destroy)
                                              ) / success_rate

            # Adjust the previous rates and two ago
            lastFailDecrease, lastFailDestroy, twoCostAgo, lastCost = fail_decrease, fail_destroy, lastCost, cost

        if checkbox_values[1] and currentStar <= 10:
            currentStar += 1  # Apply +2 stars option up to star level 9
        currentStar += 1

    answer = sum(total[StartStar + 1:TargetStar + 1])  # Sum the total costs to reach the target star level
    totalExpectedBooms = sum(expectedBooms[StartStar + 1:TargetStar + 1])
    mult = math.prod(noBoomProbs[StartStar + 1:TargetStar + 1])
    print(f"{noBoomProbs}")
    print(expectedBooms)
    result_label.config(
        # Display the result
        text=f"The expected cost is: {round(answer):,}\nExpected number of booms: {totalExpectedBooms}\nP(no Boom): {mult}")


def main():
    """
    Main function to set up the Tkinter interface and initialize the application.
    """
    root = tk.Tk()
    root.title("Starforce Calculator")
    root.geometry("1023x400")

    # Validation command for numeric input
    validate_cmd = (root.register(validate_number), '%P', '%S')

    # Set up input fields and labels
    tk.Label(root, text="Item Level").grid(row=0, column=0, padx=10, pady=10)
    entry1 = tk.Entry(root, validate="key", validatecommand=validate_cmd)
    entry1.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(root, text="MVP discount").grid(row=0, column=2, padx=10, pady=10)
    mvp_discount_options = ["None", "MVP silver (3% off 1 to 16)", "MVP gold (5% off 1 to 16)",
                            "MVP Diamond (10% off 1 to 16)"]
    mvp_discount = tk.StringVar(root)
    mvp_discount.set(mvp_discount_options[0])
    dropdown = tk.OptionMenu(root, mvp_discount, *mvp_discount_options)
    dropdown.grid(row=0, column=3, padx=10, pady=10)

    tk.Label(root, text="Current Star").grid(row=1, column=0, padx=10, pady=10)
    entry2 = tk.Entry(root, validate="key", validatecommand=validate_cmd)
    entry2.grid(row=1, column=1, padx=10, pady=10)

    tk.Label(root, text="Target Star").grid(row=1, column=2, padx=10, pady=10)
    entry3 = tk.Entry(root, validate="key", validatecommand=validate_cmd)
    entry3.grid(row=1, column=3, padx=10, pady=10)

    # Label to display the result
    result_label = tk.Label(root, text="")
    result_label.grid(row=5, columnspan=4, pady=10)

    # Calculate button to trigger the calculation
    calculate_button = tk.Button(root, text="Calculate",
                                 command=lambda: calculate_stars(entry1, entry2, entry3, result_label, checkboxes,
                                                                 mvp_discount.get()))
    calculate_button.grid(row=4, columnspan=4, pady=20)

    # Set up checkboxes for various enhancement options
    checkbox_labels = ["5/10/15", "+2 stars (up to 10)", "30% off", "Star Catching", "Safeguard"]
    checkboxes = []
    for i, label in enumerate(checkbox_labels):
        var = tk.BooleanVar(value=False)
        checkbox = tk.Checkbutton(root, text=label, variable=var)
        checkbox.grid(row=3, column=i, padx=10, pady=10)
        checkboxes.append(var)

    root.mainloop()


if __name__ == '__main__':
    main()
