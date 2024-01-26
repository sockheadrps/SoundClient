/* Copyright NoiseCrimeStudios™
 * Version: 1.0.0
 * 2023.12.17; 2023.12.14; 2023.11.28;
*/

const VERSION  = "1.0.0";
const NUM_ROWS = 200;

// CodePen - Don't forget function calls from html don't work with modules! use Events
import {maleNames} from 'https://codepen.io/Noise-Crime/pen/KKJOmOE.js';
import {countries} from 'https://codepen.io/Noise-Crime/pen/mdvNwzQ.js';
import {SimpleTable} from 'https://codepen.io/Noise-Crime/pen/LYqwxEW.js';

// EVENT FINISHED PAGE LOADING
document.addEventListener('DOMContentLoaded', () => {
  // BUTTON EVENT LISTENERS  
  document.getElementById('table-prebuilt-headers').addEventListener('click', (event) => {
    sortPrebuilt(event);
    console.log('click')
  });
  document.getElementById('run-button').addEventListener('click', (event) => {
    buildTable();
  });
});

function sortPrebuilt(event) {
  if ((event.target.type === 'button')) {
    switch (event.target.id) {
      case 'sort-0': doSort('myTable', 0); break;
      case 'sort-1': doSort('myTable', 1); break;
      case 'sort-2': doSort('myTable', 2); break;
    }
  }
}

function doSort(name, idx) {
  console.log("Not Implemented");
}

function buildTable() {  
  const element = document.getElementById("table-container");
  
  // Construct Database
  const digits = 4;
  const database = [];
  for(let i=0; i<NUM_ROWS; i++)
    database.push(new Data());
  
  // Construct Table
  const simpleTable = new SimpleTable();  
  // Construct Table Row Definitions  
  simpleTable.appendColumnDefinition("ID", digits);
  simpleTable.appendColumnDefinition("Name", 0);
  simpleTable.appendColumnDefinition("Country", 0);
  // initialise Table
  simpleTable.initTable(element, "example-table", 1, database);      
}

// Example Data class for use with SimpleTable
class Data {
  #valueB;
  #valueC;
  #status;
  
  constructor() {
    this.#valueB = maleNames[Math.floor(Math.random()*maleNames.length)]; 
    this.#valueC = countries[Math.floor(Math.random()*countries.length)];
    this.#status = [2,3,5][Math.floor(Math.random()*3)];
  }
  
 /**
 * Required by SimpleTable Module: Called to populate the cell for this row based on columnIdx.
 * @param {number} columnIdx Target column cell data - assuming object defines row data.
 * @param {number} rowIdx The row index as iterated through objectArray.
 * @param {number} digits Number of digits to zero pad the string if required.
 * @returns {string} The formatted cell data based on columnIdx.
 */
  columnData(columnIdx, rowIdx, digits) {
    switch(columnIdx) {
      case 0: return rowIdx.toString().padStart(digits, '0');
      case 1: return this.#valueB;
      case 2: return this.#valueC;
    }
    return undefined;
  }
  
 /**
 * Required by SimpleTable Module: Called to populate the <tr> class assignment.
 * @returns {string} The class assignment if any.
 */
  rowStatus() {
      switch (this.#status) {
       case 2: return "class='warning'";
       case 5: return "class='disabled'";
     }
    return "";
  }
}
