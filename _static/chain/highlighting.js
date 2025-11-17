function predecessor_info_success(predecessor, units, timeout_seconds) {
    let predecessorTransferStatus,  predecessorTransferUnits, predecessorInfo; 
    if (predecessor === 1) {
        predecessorTransferStatus = predecessor1TransferStatus;
        predecessorTransferUnits = predecessor1TransferUnits;
        predecessorInfo = predecessor1Info;
    } else {
        predecessorTransferStatus = predecessor2TransferStatus;
        predecessorTransferUnits = predecessor2TransferUnits;
        predecessorInfo = predecessor2Info;
    }
    predecessorTransferStatus.innerHTML = "<b>Request successful</b>";
    predecessorTransferUnits.innerHTML = "Inventory: +" + units;
    predecessorInfo.style.backgroundColor = "#648FFF";
    setTimeout(function () {
        predecessorTransferStatus.innerHTML = "";
        predecessorTransferUnits.innerHTML = "";
        predecessorInfo.style.backgroundColor = "";
    }, timeout_seconds * 1000);
}

function predecessor_info_failure(predecessor, timeout_seconds) {
    let predecessorTransferStatus, predecessorTransferUnits, predecessorInfo;
    if (predecessor === 1) {
        predecessorTransferStatus = predecessor1TransferStatus;
        predecessorTransferUnits = predecessor1TransferUnits;
        predecessorInfo = predecessor1Info;
    } else {
        predecessorTransferStatus = predecessor2TransferStatus;
        predecessorTransferUnits = predecessor2TransferUnits;
        predecessorInfo = predecessor2Info;
    }
    predecessorTransferStatus.innerHTML = "<b>Request failed</b>";
    predecessorTransferUnits.innerHTML = "Inventory: No change";
    predecessorInfo.style.backgroundColor = "#FFB000";
    setTimeout(function () {
        predecessorTransferStatus.innerHTML = "";
        predecessorTransferUnits.innerHTML = "";
        predecessorInfo.style.backgroundColor = "";
    }, timeout_seconds * 1000);
}

function successor_info_success(successor, units, cash, timeout_seconds) {
    let successorTransferStatus, successorTransferUnits, successorTransferCash, successorInfo;
    
    if (successor === 1) {
        successorTransferStatus = successor1TransferStatus;
        successorTransferUnits = successor1TransferUnits;
        successorTransferCash = successor1TransferCash;
        successorInfo = successor1Info;
    } else {
        successorTransferStatus = successor2TransferStatus;
        successorTransferUnits = successor2TransferUnits;
        successorTransferCash = successor2TransferCash;
        successorInfo = successor2Info;
    }
    successorTransferStatus.innerHTML = "<b>Request successful</b>";
    successorTransferUnits.innerHTML = "Inventory: -" + units;
    successorTransferCash.innerHTML = "Balance: +" + cash;
    successorInfo.style.backgroundColor = "#648FFF";
    setTimeout(function () {
        successorTransferStatus.innerHTML = "";
        successorTransferUnits.innerHTML = "";
        successorTransferCash.innerHTML = "";
        successorInfo.style.backgroundColor = "";
    }, timeout_seconds * 1000);
}

function successor_info_failure(successor, timeout_seconds) {
    let successorTransferStatus, successorTransferUnits, successorTransferCash, successorInfo;
    
    if (successor === 1) {
        successorTransferStatus = successor1TransferStatus;
        successorTransferUnits = successor1TransferUnits;
        successorTransferCash = successor1TransferCash;
        successorInfo = successor1Info;
    } else {
        successorTransferStatus = successor2TransferStatus;
        successorTransferUnits = successor2TransferUnits;
        successorTransferCash = successor2TransferCash;
        successorInfo = successor2Info;
    }
    successorTransferStatus.innerHTML = "<b>Request failed</b>";
    successorTransferUnits.innerHTML = "Inventory: No change";
    successorTransferCash.innerHTML = "Balance: No change";
    successorInfo.style.backgroundColor = "#FFB000";
    setTimeout(function () {
        successorTransferStatus.innerHTML = "";
        successorTransferUnits.innerHTML = "";
        successorTransferCash.innerHTML = "";
        successorInfo.style.backgroundColor = "";
    }, timeout_seconds * 1000);
}

function highlight_successor(successor, transferred, units, cash, timeout_seconds) {
    if (transferred) {
        successor_info_success(successor, units, cash, timeout_seconds);
    } else {
        successor_info_failure(successor, timeout_seconds);
    }
}

function highlight_predecessor(predecessor, transferred, units, timeout_seconds) {
    if (transferred) {
        predecessor_info_success(predecessor, units, timeout_seconds);
    } else {
        predecessor_info_failure(predecessor, timeout_seconds);
    }
}