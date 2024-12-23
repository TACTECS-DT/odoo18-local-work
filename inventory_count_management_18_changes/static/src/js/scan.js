/** @odoo-module */
import { registry } from "@web/core/registry";
import { loadBundle } from "@web/core/assets";
import { Component } from  "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { onWillStart,onWillRender,onRendered,onMounted,onPatched} from '@odoo/owl';
import { loadJS , loadCSS } from "@web/core/assets";

class Scanning extends Component {
    setup(parent, action){
    this.action = useService("action");
    this.orm = useService("orm");
    super.setup(parent, action);

    this.scan_data = {
        active_id: this.get_current_id(),


        all_products_data : {},
        privet_products_data : {},

        all_lots_data : {},
        privet_lots_data : {},
        
        all_internal_reference_data : {},
        privet_internal_reference_data : {},

        session_line_ids_Data: {},
        totalQty: 0,
    };
 

    onWillStart(async () => {
        await loadJS("/inventory_count_management_18_changes/static/src/js/jquery.js");
        await loadJS("/inventory_count_management_18_changes/static/src/js/bootstrap.js");
      
    });

    onMounted(async() => {
        self = this;
        return    await self.fetch_data().then(function(fitched_scan_data){
                $(document).ready(function() {
                    self.render_view(fitched_scan_data)    
                    const scanInput = document.querySelector('.scan-input');
                    // console.log(fitched_scan_data," fitched_scan_data")
                    // scanInput.addEventListener('keydown', (e) => {
                    //     if (e.key === 'Enter') { // Most barcode scanners send an Enter after the scan
                    //         self._ActionScanInput(e);
                    //         self.update_total_scanned_qty();
                    //         e.preventDefault(); // Prevent form submission or default behavior
                    //     }
                    // });


         

                    scanInput.addEventListener('change', (e) => {
                        self._ActionScanInput(e);
                        self.update_total_scanned_qty(); 
                    });

                });
         
            })
      });


}



async fetch_data() {
    let self = this;

    var fitched_scan_data = await self.orm.call('setu.inventory.count.session', 'get_lot_scan_data', [self.get_current_id()])
        .then(function(result) {
            result = JSON.parse(result);  

            self.scan_data.all_products_data = result.all_products_data;
            self.scan_data.privet_products_data = result.privet_products_data;

            self.scan_data.all_lots_data = result.all_lots_data;
            self.scan_data.privet_lots_data = result.privet_lots_data;

            self.scan_data.all_internal_reference_data = result.all_internal_reference_data;
            self.scan_data.privet_internal_reference_data = result.privet_internal_reference_data;

            


            self.scan_data.session_line_ids_Data = result.session_line_ids_Data;
            self.main_location= result.main_location;
       

            
            return result;
        });
    return fitched_scan_data;  
}



render_view(fitched_scan_data) {
    var self = this;
    self.add_scnned_from_backend(fitched_scan_data);
    self.update_total_scanned_qty();

}




add_scnned_from_backend(fitched_scan_data) {
    // Select the tbody element of the table
    let tbody = document.querySelector('.tbody');
  
    // Clear existing rows in the tbody
    tbody.innerHTML = '';
  
    // Loop through session_line_ids_Data to populate the table rows
    fitched_scan_data.session_line_ids_Data.forEach((line) => {
      // Create a new row
      let row = document.createElement('tr');
  

      // Add the ID column (hidden)
      let old_line_id = document.createElement('td');
        // Add an ID
        old_line_id.id = 'old_line_id';
        old_line_id.setAttribute('data-old-line-id', line.line_id);
        old_line_id.style.display = 'none'; // Hide the column
      row.appendChild(old_line_id);
  

      // Add the ID column (hidden)
      let idCell = document.createElement('td');
        // Add an ID
        idCell.id = 'product_id';
        idCell.setAttribute('data-product-id', line.line_product.product_id);
      idCell.style.display = 'none'; // Hide the column
      row.appendChild(idCell);
  



      let isAllCodeCell = document.createElement('td');
      isAllCodeCell.id = 'is_all_code';
      isAllCodeCell.setAttribute('data-is-all-code', line.is_all_code);
      isAllCodeCell.style.display = 'none';
      row.appendChild(isAllCodeCell);

      // Add the Product column
      let productCell = document.createElement('td');
      productCell.textContent = line.line_product.product_name;
      row.appendChild(productCell);
  
      // Add the Location column
      let locationCell = document.createElement('td');

      let locationIdSpan = document.createElement('span');
      locationIdSpan.id = 'location_id';

      locationIdSpan.style.display = 'none'; // Hide the location ID
      locationIdSpan.setAttribute('data-location-id', line.line_location.location_id);
      let locationNameSpan = document.createElement('span');
      locationNameSpan.textContent = line.line_location.location_name;
      locationCell.appendChild(locationIdSpan);
      locationCell.appendChild(locationNameSpan);
      row.appendChild(locationCell);
  
      // Add the Serial Number column
      let serialNumberCell = document.createElement('td');
      serialNumberCell.textContent = line.line_lot.lot_name
        ? line.line_lot.lot_name
        : line.line_internal_refrence;
        let lot_idSpan = document.createElement('span');
        lot_idSpan.id = 'lot_id';
        lot_idSpan.setAttribute('data-lot-id', line.line_lot.lot_id);
        serialNumberCell.appendChild(lot_idSpan);
        
      row.appendChild(serialNumberCell);
  
      // Add the Theoretical Quantity column
      let theoreticalQtyCell = document.createElement('td');
      theoreticalQtyCell.textContent = line.line_theoretical_qty;
      theoreticalQtyCell.id = 'theoretical_qty';
      theoreticalQtyCell.setAttribute('data-theoretical_qty', line.line_theoretical_qty);
  
      row.appendChild(theoreticalQtyCell);
  
      // Add the Scanned Quantity column
      let scannedQtyCell = document.createElement('td');
      let scannedQtyInput = document.createElement('input');
      scannedQtyInput.type = 'number';
      scannedQtyInput.id = 'scanned_Qty_Input';

      scannedQtyInput.className = 'form-control';
      scannedQtyInput.value = line.line_quantity;
      scannedQtyCell.appendChild(scannedQtyInput);
      row.appendChild(scannedQtyCell);
  
      // Add the Actions column
      let actionsCell = document.createElement('td');
      let deleteButton = document.createElement('button');
      deleteButton.className = 'btn btn-danger delete_row btn-sm';
      deleteButton.textContent = 'Delete';
      deleteButton.addEventListener('click', () => {
        // Remove the row when the delete button is clicked
        row.remove();
        this.update_total_scanned_qty();
      });


      scannedQtyInput.addEventListener('change', () => {
        this.update_total_scanned_qty();
    });



      actionsCell.appendChild(deleteButton);
      row.appendChild(actionsCell);
  
      // Append the row to the tbody
      tbody.appendChild(row);
    });
  }

  


_ActionScanInput(event) {
    let inputCode = event.target.value.trim(); // Get the scanned input code
    
    if (!inputCode) {
        this.show_wizard('No input code provided.',"404");
        return;
    }

    // Call the function to find where the code exists
    let foundData = this._searchForCode(inputCode);

    // If code is found, handle creating the row
    if (foundData) {
        this._createOrUpdateRowFromScan(foundData,inputCode);
    } else {

 
    const errorAudio = document.getElementById('error_audio');

        this.show_wizard('Scanned code not found!',"404");
        errorAudio.play();
    }

    event.target.value = ""; // Clear the input field after handling
}








// Separate function to search for the code
_searchForCode(inputCode) {
    let foundIn_1 = null;
    let foundIn_2 = null;
    let foundIn_3 = null;
    let foundIn_4 = null;


    let scan_msg_div= document.querySelector('.scan_msg')
    // Check in privet_lots_data
    foundIn_1 = this.scan_data.privet_lots_data.find(item => item.lot_name === inputCode);
    if (foundIn_1) {
        scan_msg_div.textContent = "Product  in your stock (Lot)"
        scan_msg_div.style.color = "green";
        return { source: "privet_lots_data", data: foundIn_1 };
    }

    // Check in privet_internal_reference_data
    foundIn_2 = this.scan_data.privet_internal_reference_data.find(item => item.internal_reference === inputCode);
    if (foundIn_2) {
        scan_msg_div.textContent = "Product  in your stock (Internal reference)"
        scan_msg_div.style.color = "green";
        return { source: "privet_internal_reference_data", data: foundIn_2 };
    }

if(!foundIn_1 && !foundIn_2) {
    // Check in all_lots_data
    foundIn_3 = this.scan_data.all_lots_data.find(item => item.lot_name === inputCode);
    if (foundIn_3) {
        scan_msg_div.textContent = "Product  not in your stock (Lot)"
        scan_msg_div.style.color = "red";
        return { source: "all_lots_data", data: foundIn_3 };
    }

    // Check in all_internal_reference_data
    foundIn_4 = this.scan_data.all_internal_reference_data.find(item => item.internal_reference === inputCode);
    if (foundIn_4) {
        scan_msg_div.textContent = "Product not in your stock (Internal reference)"
        scan_msg_div.style.color = "red";
        return { source: "all_internal_reference_data", data: foundIn_4 };
    }
}
    return null;
}









_createOrUpdateRowFromScan(foundData ,scanned_code) {


    // Get references to the audio elements
    const scanAudio = document.getElementById('scan_audio');
    const warningAudio = document.getElementById('warning_audio');
    const errorAudio = document.getElementById('error_audio');
    

    let { source, data } = foundData;
    let tbody = document.querySelector('.tbody');

    // Get necessary data for the row
    let productId = data.product.product_id;
    let productName = data.product.product_name;



    let p_internal_reference = source === "privet_internal_reference_data" || source === "all_internal_reference_data"
        ? data.internal_reference
        : data.product.internal_reference;

    
    // console.log(scanned_code,'scanned_code')
    // console.log(foundData,"foundData")
    // console.log(p_internal_reference,"p_internal_reference")
    let r_lot_id =  source === "all_lots_data" || source === "privet_lots_data"
    ? data.lot_id
    : false;
    let r_lot_name =  source === "all_lots_data" || source === "privet_lots_data"
    ? data.lot_name
    : false;

    // console.log(r_lot_name,"r_lot_name")
    // console.log(r_lot_id,"lot_id")

    let line_location_id = this.main_location.location_id;
    let line_location_name = this.main_location.location_name;

    if (source === "privet_lots_data" || source === "privet_internal_reference_data") {



let existingRows;

if (source === "privet_lots_data") {

/*
 filters :
 productId = productId
 is_all_code = 0  //privet 
 data-lot-id = lot_id 
*/



    existingRows = Array.from(tbody.querySelectorAll(`[data-product-id="${productId}"]`)).map(cell => cell.closest('tr')) 

        .filter(row => {
            let isAllCodeInRow = row.querySelector('#is_all_code');
            
        // if (!isAllCodeInRow) {
        //     return false; // Exclude rows without this <td>
        // }
            const lotSpan = row.querySelector('span#lot_id');
            return lotSpan && lotSpan.getAttribute('data-lot-id')== r_lot_id  && isAllCodeInRow.getAttribute('data-is-all-code') ==='0';
        });
} 


else if (source === "privet_internal_reference_data") {

/*
 filters :
 productId = productId
 is_all_code = 0  //privet 
 data-lot-id = 'false' 
 must have is_all_code to avoid old scan lines
*/

existingRows = Array.from(tbody.querySelectorAll(`[data-product-id="${productId}"]`))
    .map(cell => cell.closest('tr')).filter(row => {
        let isAllCodeInRow = row.querySelector('#is_all_code');

        // if (!isAllCodeInRow) {
        //     return false; // Exclude rows without this <td>
        // }
        const lotId = row.querySelector('[data-lot-id]')?.getAttribute('data-lot-id');
        return lotId === 'false' && isAllCodeInRow.getAttribute('data-is-all-code') ==='0';
    });


}


        if (existingRows.length > 0) {
            let firstRow = existingRows[0].closest('tr');
            // console.log(firstRow,"firstRow")
            let scannedQtyInput = firstRow.querySelector('#scanned_Qty_Input');
            scannedQtyInput.value = parseInt(scannedQtyInput.value, 10) + 1; // Increment by 1

            if (existingRows.length > 1) {
                console.warn(`More than one row found for product_id: ${productId}. Quantity updated only in the first row.`);
            }
            console.log("source xxx" , source)
            if (source==='privet_lots_data' || source ==="privet_internal_reference_data"){
                scanAudio.play();  
              }
        
            
            if (source==='all_lots_data' || source ==="all_internal_reference_data"){
                warningAudio .play();  
              }
        
            this.set_last_scan(scanned_code, productName, p_internal_reference);
        } else {
            // Add a new row if no existing row found
            this._addRowToTable({
                tbody,
                productId,
                productName,
                p_internal_reference,
                r_lot_id,
                r_lot_name,
                theoreticalQty: this.scan_data.privet_products_data.find(product => product.product_id === productId)?.quantity || 0,
                is_all_code: 0,
                line_location_id,
                line_location_name,
                
            },scanned_code,source);
        }
    }
    
    
    else if (source === "all_lots_data" || source === "all_internal_reference_data") {

        let rowsWithCode = Array.from(tbody.querySelectorAll('td')).filter(row => row.hasAttribute('data-is-all-code'));
        

        let existingRow;

        if (source === "all_lots_data") {
       
/*
 filters :
 productId = productId
 is_all_code = 1  //all 
 data-lot-id = lot_id
*/



             existingRow = rowsWithCode.find(row => {
                let isAllCodeInRow = row.getAttribute('data-is-all-code');
                let productIdInRow = row.closest('tr').querySelector('[data-product-id]')?.getAttribute('data-product-id');
                // if (!isAllCodeInRow) {
                //     return false; // Exclude rows without this <td>
                // }
                let rowLot_id = row.closest('tr').querySelector('[data-lot-id]')?.getAttribute('data-lot-id');


                return isAllCodeInRow === '1' && productIdInRow === productId.toString()  && rowLot_id === r_lot_id.toString() ;
            });
        
            

        } 
        
        
        else if (source === "all_internal_reference_data") {

/*
 filters :
 productId = productId
 is_all_code = 1  //all 
 data-lot-id = 'false'
*/



         existingRow = rowsWithCode.find(row => {
            let rowLot_id = row.closest('tr').querySelector('[data-lot-id]')?.getAttribute('data-lot-id');

        let isAllCodeInRow = row.getAttribute('data-is-all-code');
        // if (!isAllCodeInRow) {
        //     return false; // Exclude rows without this <td>
        // }
        let productIdInRow = row.closest('tr').querySelector('[data-product-id]')?.getAttribute('data-product-id');
        return isAllCodeInRow === '1' && productIdInRow === productId.toString()  && rowLot_id === 'false' ;
    });


        }


        if (existingRow) {
            existingRow = existingRow.closest('tr')
            let scannedQtyInput = existingRow.querySelector('#scanned_Qty_Input');
            scannedQtyInput.value = parseInt(scannedQtyInput.value, 10) + 1; // Increment by 1
            this.set_last_scan(scanned_code, productName, p_internal_reference);





            console.log("source xxx" , source)
            if (source==='privet_lots_data' || source ==="privet_internal_reference_data"){
                scanAudio.play();  
              }
        
            
            if (source==='all_lots_data' || source ==="all_internal_reference_data"){
                warningAudio .play();  
              }
        


        } else {
            // Add a new row if no existing row found
            this._addRowToTable({
                tbody,
                productId,
                productName,
                p_internal_reference,
                r_lot_id,
                r_lot_name,
                theoreticalQty: 0,
                is_all_code: 1,
                line_location_id,
                line_location_name,
                
            },scanned_code,source);
        }
    }
}

// Separate function to add a row to the table
_addRowToTable({ tbody, productId, productName, p_internal_reference,  r_lot_id,
    r_lot_name,theoreticalQty, is_all_code, line_location_id, line_location_name },scanned_code,source) {
    let row = document.createElement('tr');


    let isAllCodeCell = document.createElement('td');
    isAllCodeCell.id = 'is_all_code';
    isAllCodeCell.setAttribute('data-is-all-code', is_all_code);
    isAllCodeCell.style.display = 'none';
    row.appendChild(isAllCodeCell);

    // Hidden column for product ID
    let productIdCell = document.createElement('td');
    productIdCell.id = 'product_id';
    productIdCell.setAttribute('data-product-id', productId);
    productIdCell.style.display = 'none';
    row.appendChild(productIdCell);

    // Product Name
    let productNameCell = document.createElement('td');
    productNameCell.textContent = productName;
    row.appendChild(productNameCell);

    // Location
    let locationCell = document.createElement('td');
    locationCell.textContent = line_location_name;
    row.appendChild(locationCell);

    // Serial/Reference Number
    let serialCell = document.createElement('td');
    serialCell.textContent =   source === "all_lots_data" || source === "privet_lots_data"
    ? r_lot_name
    : p_internal_reference;
    // console.log(source,"r_source 2 ")
    // console.log(r_lot_name,"r_lot_name 2 ")
    // console.log(p_internal_reference,"p_internal_reference 2 ")

    let lot_idSpan = document.createElement('span');
    lot_idSpan.id = 'lot_id';
    lot_idSpan.setAttribute('data-lot-id', r_lot_id);
    serialCell.appendChild(lot_idSpan);

    row.appendChild(serialCell);





    // Theoretical Quantity
    let theoreticalQtyCell = document.createElement('td');
    theoreticalQtyCell.textContent = theoreticalQty;
    
    theoreticalQtyCell.id = 'theoretical_qty';
    theoreticalQtyCell.setAttribute('data-theoretical_qty', theoreticalQty);

    row.appendChild(theoreticalQtyCell);

    // Scanned Quantity
    let scannedQtyCell = document.createElement('td');
    let scannedQtyInput = document.createElement('input');
    scannedQtyInput.type = 'number';
    scannedQtyInput.id = 'scanned_Qty_Input';
    scannedQtyInput.className = 'form-control';
    scannedQtyInput.value = 1;
    scannedQtyCell.appendChild(scannedQtyInput);
    row.appendChild(scannedQtyCell);

    scannedQtyInput.addEventListener('change', () => {
        this.update_total_scanned_qty();
    });

    // Actions (Delete button)
    let actionsCell = document.createElement('td');
    let deleteButton = document.createElement('button');
    deleteButton.className = 'btn btn-danger delete_row btn-sm';
    deleteButton.textContent = 'Delete';
    deleteButton.addEventListener('click', () => {
        row.remove();
        this.update_total_scanned_qty();
    });
    actionsCell.appendChild(deleteButton);
    row.appendChild(actionsCell);

    // Append the row to the table body
    tbody.appendChild(row);

    this.update_total_scanned_qty();
    this.set_last_scan(scanned_code, productName, p_internal_reference);



    // Get references to the audio elements
    const scanAudio = document.getElementById('scan_audio');
    const warningAudio = document.getElementById('warning_audio');

    console.log("source xxx" , source)
    if (source==='privet_lots_data' || source ==="privet_internal_reference_data"){
        scanAudio.play();  
      }

    
    if (source==='all_lots_data' || source ==="all_internal_reference_data"){
        warningAudio .play();  
      }




}
















set_last_scan(scannedCode,productName,p_internal_reference){
   let  last_scan_div= document.querySelector(".last_scan")
    let last_scan_product= last_scan_div.querySelector(".last_scan_product")
    let last_scan_lot= last_scan_div.querySelector(".last_scan_lot")
    let last_scan_internal_ref= last_scan_div.querySelector(".last_scan_internal_ref")


    last_scan_product.textContent = productName;
    last_scan_lot.textContent = scannedCode;
    last_scan_internal_ref.textContent = p_internal_reference;


    
}



update_total_scanned_qty() {
    const scannedQtyInputs = document.querySelectorAll('#scanned_Qty_Input');
    let totalQty = 0;
    scannedQtyInputs.forEach(input => {
        totalQty += parseInt(input.value, 10) || 0; // Ensure no NaN values
    });
    // Update the footer with the total quantity
    document.getElementById('total-scanned-qty').textContent = totalQty;
    document.getElementById('total-scanned-qty2').textContent = totalQty;
}


cancel_button () {
    var self = this;

    self.action.doAction({
        type: 'ir.actions.act_window',
        res_model: 'setu.inventory.count.session',
        res_id: parseInt(self.scan_data.active_id),          
        views: [[false, 'form']],
        target: 'main',
    });
}


 async save_button (e) {
    var self = this;
    let scannedData= self.collect_table_vals()
    // console.log(scannedData); 
    if (scannedData && (
        (Array.isArray(scannedData) && scannedData.length > 0) || 
        (typeof scannedData === 'object' && Object.keys(scannedData).length > 0)
    ))
    
    {  
        
    let save_data = await self.orm.call('setu.inventory.count.session', 'save_scanned_data', [scannedData,this.scan_data.active_id])
    .then(function(result) {
        if (result ==="done"){
            
    // self.show_wizard("done", "saved");
            self.cancel_button()
        }
        else{
    self.show_wizard(result, "Error");

        }


    });
    }
    else{
        this.show_wizard("no data to save","No Data")
    }

}


collect_table_vals() {
    // Initialize an array to hold the scanned data
    let Data = [];

    // Get all the rows from the tbody
    let rows = document.querySelectorAll('.tbody tr');

    // Iterate over each row to extract the product_id and scanned_Qty_Input
    rows.forEach(row => {


           // Check for the presence of 'old_line_id'
           let oldLineId = row.querySelector('[data-old-line-id]');

           let old_line_id = oldLineId ? parseInt(oldLineId.getAttribute('data-old-line-id'), 10) : "none";


           


        // Get product_id from the hidden td (data-product-id)
        let productId = row.querySelector('[data-product-id]').getAttribute('data-product-id');
        
        // Get scanned quantity input value
        let scannedQty = parseInt(row.querySelector('#scanned_Qty_Input').value, 10) || 0;
        let theoretical_qty = parseInt(row.querySelector('#theoretical_qty').getAttribute('data-theoretical_qty'), 10) || 0;
        let lot_id = parseInt(row.querySelector('#lot_id').getAttribute('data-lot-id'), 10) || 0;
        
        // Add the data to the scannedData array
        Data.push({
            "product_id": productId,
            "qty": scannedQty,
            "old_line_id": old_line_id,
            "theoretical_qty": theoretical_qty,
            "lot_id": lot_id
        });
    });

    return Data
    }




show_wizard(message,header) {
    // Update the message dynamically
    const messageElement = document.querySelector('#scan_wizard .massage');
    const modaltitle = document.querySelector('#scan_wizard .modal-title');

    messageElement.textContent = message; 
    modaltitle.textContent = header; 


    // Get modal element
    const modalElement = document.querySelector('#scan_wizard');
    
    // Initialize Bootstrap modal if not initialized
    const modal = new bootstrap.Modal(modalElement);
    
    // Show the modal
    modal.show();
}



get_current_id () {
    let c_id =this.props.action.context.active_id
    return c_id;
}



}


Scanning.template = "Scanning";
registry.category("actions").add("stock.scan", Scanning);

