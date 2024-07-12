function getCost(curr, lvl, discount, options) {
    let cost;
    if (curr < 10) {
        cost = 100 * Math.round((lvl ** 3) * (curr + 1) / 2500 + 10) * discount;
    } else if (curr < 15) {
        const divisors = [40000, 22000, 15000, 11000, 7500];
        cost = 100 * Math.round((lvl ** 3) * (curr + 1) ** 2.7 / divisors[curr - 10] + 10) * discount;
    } else {
        cost = 100 * Math.round((lvl ** 3) * (curr + 1) ** 2.7 / 20000 + 10) * discount;
    }

    if (options[4] && (curr === 15 || curr === 16)) {
        if (!(options[0] && curr === 15)) {
            cost *= 2;
        }
    }

    return cost;
}

function getSuccess(curr, odds, options) {
    let success = odds[0][curr] * (options[3] ? 1.05 : 1);
    let total_fail_rate = 1 - success;
    let maintain = total_fail_rate * odds[1][curr];
    let decrease = total_fail_rate * odds[2][curr];
    let boom = total_fail_rate * odds[3][curr];

    if (options[4] && (curr === 15 || curr === 16)) {
        if (maintain !== 0) {
            maintain += boom;
        } else {
            decrease += boom;
        }
        boom = 0;
    }

    if (options[0] && (curr === 5 || curr === 10 || curr === 15)) {
        success = 1;
        maintain = 0;
        decrease = 0;
        boom = 0;
    }

    return [success, maintain, decrease, boom];
}

function calculateStars() {
    const itemLevel = parseInt(document.getElementById('itemLevel').value);
    const currentStar = parseInt(document.getElementById('currentStar').value);
    const targetStar = parseInt(document.getElementById('targetStar').value);
    const mvpDiscount = parseFloat(document.getElementById('mvpDiscount').value);

    const options = [
        document.getElementById('option1').checked,
        document.getElementById('option2').checked,
        document.getElementById('option3').checked,
        document.getElementById('option4').checked,
        document.getElementById('option5').checked
    ];

    if (isNaN(itemLevel) || isNaN(currentStar) || isNaN(targetStar) || targetStar < currentStar || targetStar > 25) {
        document.getElementById('result').innerText = 'Invalid input';
        return;
    }

    const baseOdds = [
        [.95, .9, .85, .85, .8, .75, .7, .65, .6, .55, .5, .45, .4, .35, .3, .3, .3, .3, .3, .3, .3, .3, .03, .02, .01],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, .97, 0, 0, 0, 0, .9, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, .97, .97, .96, .96, 0, .9, .8, .7, .6],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, .03, .03, .03, .04, .04, .1, .1, .2, .3, .4]
    ];

    let total = Array(26).fill(0);
    let currStar = currentStar;
    let lastFailDecrease, lastFailDestroy, twoCostAgo, lastCost = 0;

    while (currStar < targetStar) {
        let mvp = currStar <= 15 ? mvpDiscount : 0;
        let discount = options[2] ? 0.7 * (1 - mvp) : 1 - mvp;

        let [success, failMaintain, failDecrease, failDestroy] = getSuccess(currStar, baseOdds, options);
        let cost = getCost(currStar, itemLevel, discount, options);

        if (currStar < 15) {
            total[currStar + 1] = cost / success;
        } else if (currStar === 15 || currStar === 20) {
            total[currStar + 1] = (cost + failDestroy * total.slice(13, currStar + 1).reduce((a, b) => a + b, 0)) / success;
            [lastFailDecrease, lastFailDestroy, twoCostAgo, lastCost] = [failDecrease, failDestroy, lastCost, cost];
        } else if (currStar === 16 || currStar === 21) {
            total[currStar + 1] = (cost + failDecrease * total[currStar] + failDestroy * total.slice(13, currStar + 1).reduce((a, b) => a + b, 0)) / success;
            [lastFailDecrease, lastFailDestroy, twoCostAgo, lastCost] = [failDecrease, failDestroy, lastCost, cost];
        } else {
            total[currStar + 1] = (cost + failDecrease * lastCost + failDecrease * lastFailDecrease * (twoCostAgo + total[currStar]) + (failDecrease * lastFailDestroy + failDestroy) * total.slice(13, currStar + 1).reduce((a, b) => a + b, 0)) / success;
            [lastFailDecrease, lastFailDestroy, twoCostAgo, lastCost] = [failDecrease, failDestroy, lastCost, cost];
        }

        if (options[1] && currStar <= 10) {
            currStar += 1;
        }
        currStar += 1;
    }

    let answer = total.slice(currentStar + 1, targetStar + 1).reduce((a, b) => a + b, 0);
    document.getElementById('result').innerText = `The expected cost is: ${Math.round(answer).toLocaleString()}\nMVP Discount: ${document.getElementById('mvpDiscount').selectedOptions[0].text}\nOptions: ${options}`;
}
