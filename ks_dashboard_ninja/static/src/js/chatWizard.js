///** @odoo-module **/
//
//import { Component, onWillStart, useState } from "@odoo/owl";
//import { useService } from "@web/core/utils/hooks";
//import { Dialog } from "@web/core/dialog/dialog";
//import { Thread } from "@mail/core/common/thread";
//import { Composer } from "@mail/core/common/composer";
//import { rpc } from "@web/core/network/rpc";
//import {
//    useMessageEdition,
//    useMessageHighlight,
//    useMessageToReplyTo,
//} from "@mail/utils/common/hooks";
//
//export class chatWizard extends Component{
//
//    setup(){
//        this.threadService = useService("mail.store");
//        this.channelModel = 'discuss.channel';
//        this.channelModelId = null;
//        this.messageEdition = useMessageEdition();
//        this.messageToReplyTo = useMessageToReplyTo();
//        this.state = useState({ jumpThreadPresent: 0 });
//
//        onWillStart( async() => {
//            try{
//                const channelModelId = await rpc("/web/dataset/call_kw/discuss.channel/getId",{
//                model: 'discuss.channel',
//                method: 'ks_chat_wizard_channel_id',
//                args: [[]],
//                kwargs:{
//                        item_id: this.props.itemId,
//                        dashboard_id: this.props.dashboardId,
//                        dashboard_name: this.props.dashboardName,
//                        item_name: this.props.itemName,
//                    }
//                });
//
//                this.channelModelId = channelModelId;
//            }
//            catch(error){
//                this.channelModelId = null;
//            }
//        });
//    }
//
//    get thread(){
//        if(this.channelModel && this.channelModelId)
//            return this.threadService.Thread.insert({ model: this.channelModel, id: this.channelModelId });
//        else
//            return false;
//    }
//
//}
//
//chatWizard.template = "ks_dashboard_ninja.chat_wizard"
//
//chatWizard.components = { Dialog, Thread, Composer }
