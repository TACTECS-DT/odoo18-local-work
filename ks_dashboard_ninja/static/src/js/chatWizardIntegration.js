/** @odoo-module **/

import { chatWizard } from '@ks_dashboard_ninja/js/chatWizard';
import { Ksdashboardgraph } from '@ks_dashboard_ninja/components/ks_dashboard_graphs/ks_dashboard_graphs';
import { Ksdashboardtodo } from '@ks_dashboard_ninja/components/ks_dashboard_to_do_item/ks_dashboard_to_do';
import { Ksdashboardtile } from '@ks_dashboard_ninja/components/ks_dashboard_tile_view/ks_dashboard_tile';
import { patch } from "@web/core/utils/patch";
import { rpc } from "@web/core/network/rpc";
import { Ksdashboardkpiview } from '@ks_dashboard_ninja/components/ks_dashboard_kpi_view/ks_dashboard_kpi';

patch(Ksdashboardgraph.prototype,{

    async _openChatWizard(ev){
        ev.stopPropagation();
        let internal_chat_thread;
        let channelId = await rpc("/web/dataset/call_kw/discuss.channel/getId",{
            model: 'discuss.channel',
            method: 'ks_chat_wizard_channel_id',
            args: [[]],
            kwargs:{
                item_id: this.item.id,
                dashboard_id: this.ks_dashboard_id,
                dashboard_name: this.ks_dashboard_data.name,
                item_name: this.item.name,
            }
        })
        if(channelId)   internal_chat_thread = this.env.services["mail.store"].Thread.insert({
            model: "discuss.channel",
            id: channelId,
        });
        if(internal_chat_thread){
            this.storeService.chatHub?.opened.add({ thread: internal_chat_thread })
        }

    }
});

patch(Ksdashboardkpiview.prototype,{

    async _openChatWizard(ev){
        ev.stopPropagation();
        let internal_chat_thread;
        let channelId = await rpc("/web/dataset/call_kw/discuss.channel/getId",{
            model: 'discuss.channel',
            method: 'ks_chat_wizard_channel_id',
            args: [[]],
            kwargs:{
                item_id: this.item.id,
                dashboard_id: this.ks_dashboard_id,
                dashboard_name: this.ks_dashboard_data.name,
                item_name: this.item.name,
            }
        })
        if(channelId)   internal_chat_thread = this.env.services["mail.store"].Thread.insert({
            model: "discuss.channel",
            id: channelId,
        });
        if(internal_chat_thread)
            this.storeService.chatHub?.opened.add({ thread: internal_chat_thread })
    }
});


patch(Ksdashboardtodo.prototype,{

    async _openChatWizard(ev){
        ev.stopPropagation();
        let internal_chat_thread;
        let channelId = await rpc("/web/dataset/call_kw/discuss.channel/getId",{
            model: 'discuss.channel',
            method: 'ks_chat_wizard_channel_id',
            args: [[]],
            kwargs:{
                item_id: this.item.id,
                dashboard_id: this.ks_dashboard_id,
                dashboard_name: this.ks_dashboard_data.name,
                item_name: this.item.name,
            }
        })
       if(channelId)   internal_chat_thread = this.env.services["mail.store"].Thread.insert({
            model: "discuss.channel",
            id: channelId,
        });
        if(internal_chat_thread)
            this.storeService.chatHub?.opened.add({ thread: internal_chat_thread })
    }
});

patch(Ksdashboardtile.prototype,{

    async _openChatWizard(ev){
        ev.stopPropagation();
        let internal_chat_thread;
        let channelId = await rpc("/web/dataset/call_kw/discuss.channel/getId",{
            model: 'discuss.channel',
            method: 'ks_chat_wizard_channel_id',
            args: [[]],
            kwargs:{
                item_id: this.item.id,
                dashboard_id: this.ks_dashboard_id,
                dashboard_name: this.ks_dashboard_data.name,
                item_name: this.item.name,
            }
        })
        if(channelId)   internal_chat_thread = this.env.services["mail.store"].Thread.insert({
            model: "discuss.channel",
            id: channelId,
        });
        if(internal_chat_thread)
            this.storeService.chatHub?.opened.add({ thread: internal_chat_thread })
    }
});

