/** @odoo-module **/
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";
const { Component,useRef,useState,onWillStart } = owl;

export class KsKeywordSelection extends Component {
    static template = 'KsKeywordSelection';
    setup() {
        super.setup();
        this.props.record.data.ks_import_id;
        this.input = useRef('ks_input');
        this.search = useRef('ks_search');
        this.ks_sample_final_data = [];
        this.state = useState({ values: []});
//        this.sharedState = useService("shared_state");
//        this.state.values = this.sharedState.getValue();
        onWillStart(async()=>{
            this.ks_data_model = await rpc('/web/dataset/call_kw/ks_dashboard_ninja.arti_int/ks_get_keywords',{
                model:'ks_dashboard_ninja.arti_int',
                method:'ks_get_keywords',
                args:[],
                kwargs: {},
            })
            this.state.values = this.ks_data_model;
        });
    }

    _onKeyup(ev) {
        var value = ev.target.value;
        var self=this;
        var ks_active_target = self.search.el?.querySelectorAll(".active");
        if (value.length){
            var ks_value = value.toUpperCase();
            self.state.values =[];
            if (this.ks_data_model){
                this.ks_data_model.forEach((item) =>{
                    if (item.value.toUpperCase().indexOf(ks_value) >-1 && item.value !== value){
                        self.state.values.push(item)
                    }
                })
                self.state.values.splice(0,0,{"value":value,'id':0})

                self.search.el?.classList.remove('d-none');
                self.search.el?.classList.add('d-block');
            }
        }else{
            this.state.values = this.ks_data_model
            self.search.el?.classList.remove('d-none');
            self.search.el?.classList.add('d-block');
            this.props.record.update({[this.props.name]: ""})
        }
    }

   _onResponseSelect(ev) {
        var self = this;
         var value = ev.currentTarget.querySelector(".ai-title").textContent;
         this.props.record.update({[this.props.name]: value });
//        self.props.update(value);
         this.input.el.value = value;
         document.querySelectorAll('#ks_keywords_container .createAI-card').forEach(function(element) {
            if (element.classList.contains('active')) {
                element.classList.remove('active');
            }
         });
         ev.currentTarget.classList.add("active");
    }

}
export const KsKeywordSelectionfield = {
    component: KsKeywordSelection,
}

registry.category("fields").add('ks_keyword_selection', KsKeywordSelectionfield);

