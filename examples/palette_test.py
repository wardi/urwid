#!/usr/bin/env python
#
# Urwid Palette Test.  Showing off highcolor support
#    Copyright (C) 2004-2009  Ian Ward
#
#    This library is free software; you can redistribute it and/or
#    modify it under the terms of the GNU Lesser General Public
#    License as published by the Free Software Foundation; either
#    version 2.1 of the License, or (at your option) any later version.
#
#    This library is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with this library; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Urwid web site: https://urwid.org/

"""
Palette test.  Shows the available foreground and background settings
in monochrome, 16 color, 88 color, 256 color, and 24-bit (true) color modes.
"""

from __future__ import annotations

import re

import urwid
import urwid.raw_display

CHART_TRUE = """
#e50000#e51000#e52000#e53000#e54000#e55000#e56000#e57000#e58000#e59000\
#e5a000#e5b100#e5c100#e5d100#e5e100#d9e500#c9e500#b9e500#a9e500#99e500\
#89e500#79e500#68e500#58e500#48e500#38e500#28e500#18e500#08e500#00e507\
#00e517#00e527#00e538#00e548#00e558#00e568#00e578#00e588#00e598#00e5a8\
#00e5b8#00e5c8#00e5d8#00e1e5#00d1e5#00c1e5#00b1e5#00a1e5#0091e5#0081e5\
#0071e5#0061e5#0051e5#0040e5#0030e5#0020e5#0010e5#0000e5#0f00e5#1f00e5\
#2f00e5#3f00e5#4f00e5#5f00e5#7000e5#8000e5#9000e5#a000e5#b000e5#c000e5\
#d000e5#e000e5#e500da#e500ca#e500b9#e500a9#e50099#e50089
#da0000#da0f00#da1e00#da2e00#da3d00#da4c00#da5c00#da6b00#da7a00#da8a00\
#da9900#daa800#dab800#dac700#dad600#cfda00#c0da00#b0da00#a1da00#92da00\
#82da00#73da00#64da00#54da00#45da00#35da00#26da00#17da00#07da00#00da07\
#00da16#00da26#00da35#00da44#00da54#00da63#00da72#00da82#00da91#00daa0\
#00dab0#00dabf#00dace#00d7da#00c8da#00b8da#00a9da#0099da#008ada#007bda\
#006bda#005cda#004dda#003dda#002eda#001fda#000fda#0000da#0e00da#1e00da\
#2d00da#3c00da#4c00da#5b00da#6a00da#7a00da#8900da#9800da#a800da#b700da\
#c600da#d600da#da00cf#da00c0#da00b1#da00a1#da0092#da0083
#d00000#d00e00#d01d00#d02b00#d03a00#d04800#d05700#d06600#d07400#d08300\
#d09100#d0a000#d0af00#d0bd00#d0cc00#c5d000#b6d000#a8d000#99d000#8ad000\
#7cd000#6dd000#5fd000#50d000#41d000#33d000#24d000#16d000#07d000#00d007\
#00d015#00d024#00d032#00d041#00d04f#00d05e#00d06d#00d07b#00d08a#00d098\
#00d0a7#00d0b6#00d0c4#00ccd0#00bed0#00afd0#00a1d0#0092d0#0083d0#0075d0\
#0066d0#0058d0#0049d0#003ad0#002cd0#001dd0#000fd0#0000d0#0e00d0#1c00d0\
#2b00d0#3900d0#4800d0#5600d0#6500d0#7400d0#8200d0#9100d0#9f00d0#ae00d0\
#bd00d0#cb00d0#d000c5#d000b7#d000a8#d00099#d0008b#d0007c
#c50000#c50d00#c51b00#c52900#c53700#c54500#c55300#c56000#c56e00#c57c00\
#c58a00#c59800#c5a600#c5b300#c5c100#bbc500#adc500#9fc500#91c500#83c500\
#75c500#68c500#5ac500#4cc500#3ec500#30c500#22c500#15c500#07c500#00c506\
#00c514#00c522#00c530#00c53e#00c54b#00c559#00c567#00c575#00c583#00c591\
#00c59e#00c5ac#00c5ba#00c2c5#00b4c5#00a6c5#0098c5#008ac5#007dc5#006fc5\
#0061c5#0053c5#0045c5#0037c5#002ac5#001cc5#000ec5#0000c5#0d00c5#1b00c5\
#2800c5#3600c5#4400c5#5200c5#6000c5#6e00c5#7c00c5#8900c5#9700c5#a500c5\
#b300c5#c100c5#c500bb#c500ad#c5009f#c50092#c50084#c50076
#ba0000#ba0d00#ba1a00#ba2700#ba3400#ba4100#ba4e00#ba5b00#ba6800#ba7500\
#ba8200#ba8f00#ba9c00#baaa00#bab700#b0ba00#a3ba00#96ba00#89ba00#7cba00\
#6fba00#62ba00#55ba00#48ba00#3bba00#2eba00#20ba00#13ba00#06ba00#00ba06\
#00ba13#00ba20#00ba2d#00ba3a#00ba47#00ba54#00ba61#00ba6e#00ba7c#00ba89\
#00ba96#00baa3#00bab0#00b7ba#00aaba#009dba#0090ba#0083ba#0076ba#0069ba\
#005cba#004eba#0041ba#0034ba#0027ba#001aba#000dba#0000ba#0c00ba#1900ba\
#2600ba#3300ba#4000ba#4e00ba#5b00ba#6800ba#7500ba#8200ba#8f00ba#9c00ba\
#a900ba#b600ba#ba00b1#ba00a4#ba0097#ba008a#ba007d#ba006f
#af0000#af0c00#af1800#af2400#af3100#af3d00#af4900#af5600#af6200#af6e00\
#af7b00#af8700#af9300#afa000#afac00#a6af00#9aaf00#8eaf00#81af00#75af00\
#69af00#5caf00#50af00#44af00#37af00#2baf00#1faf00#12af00#06af00#00af05\
#00af12#00af1e#00af2a#00af37#00af43#00af4f#00af5c#00af68#00af74#00af81\
#00af8d#00af99#00afa6#00adaf#00a0af#0094af#0088af#007baf#006faf#0063af\
#0056af#004aaf#003eaf#0031af#0025af#0019af#000caf#0000af#0b00af#1800af\
#2400af#3000af#3d00af#4900af#5500af#6200af#6e00af#7a00af#8700af#9300af\
#9f00af#ac00af#af00a7#af009a#af008e#af0082#af0075#af0069
#a50000#a50b00#a51700#a52200#a52e00#a53900#a54500#a55100#a55c00#a56800\
#a57300#a57f00#a58a00#a59600#a5a200#9ca500#90a500#85a500#79a500#6ea500\
#62a500#57a500#4ba500#3fa500#34a500#28a500#1da500#11a500#06a500#00a505\
#00a511#00a51c#00a528#00a533#00a53f#00a54b#00a556#00a562#00a56d#00a579\
#00a584#00a590#00a59c#00a2a5#0096a5#008ba5#007fa5#0074a5#0068a5#005da5\
#0051a5#0045a5#003aa5#002ea5#0023a5#0017a5#000ca5#0000a5#0b00a5#1600a5\
#2200a5#2d00a5#3900a5#4500a5#5000a5#5c00a5#6700a5#7300a5#7e00a5#8a00a5\
#9600a5#a100a5#a5009c#a50091#a50085#a5007a#a5006e#a50063
#9a0000#9a0a00#9a1500#9a2000#9a2b00#9a3600#9a4000#9a4b00#9a5600#9a6100\
#9a6c00#9a7700#9a8100#9a8c00#9a9700#929a00#879a00#7c9a00#719a00#679a00\
#5c9a00#519a00#469a00#3b9a00#309a00#269a00#1b9a00#109a00#059a00#009a05\
#009a10#009a1a#009a25#009a30#009a3b#009a46#009a50#009a5b#009a66#009a71\
#009a7c#009a87#009a91#00979a#008d9a#00829a#00779a#006c9a#00619a#00569a\
#004c9a#00419a#00369a#002b9a#00209a#00169a#000b9a#00009a#0a009a#15009a\
#20009a#2a009a#35009a#40009a#4b009a#56009a#61009a#6b009a#76009a#81009a\
#8c009a#97009a#9a0092#9a0087#9a007d#9a0072#9a0067#9a005c
#8f0000#8f0a00#8f1400#8f1e00#8f2800#8f3200#8f3c00#8f4600#8f5000#8f5a00\
#8f6400#8f6e00#8f7800#8f8200#8f8c00#888f00#7e8f00#748f00#698f00#5f8f00\
#558f00#4b8f00#418f00#378f00#2d8f00#238f00#198f00#0f8f00#058f00#008f04\
#008f0e#008f18#008f23#008f2d#008f37#008f41#008f4b#008f55#008f5f#008f69\
#008f73#008f7d#008f87#008d8f#00838f#00798f#006f8f#00658f#005b8f#00508f\
#00468f#003c8f#00328f#00288f#001e8f#00148f#000a8f#00008f#09008f#13008f\
#1d008f#27008f#31008f#3c008f#46008f#50008f#5a008f#64008f#6e008f#78008f\
#82008f#8c008f#8f0088#8f007e#8f0074#8f006a#8f0060#8f0056
#840000#840900#841200#841b00#842500#842e00#843700#844100#844a00#845300\
#845d00#846600#846f00#847900#848200#7d8400#748400#6b8400#628400#588400\
#4f8400#468400#3c8400#338400#2a8400#208400#178400#0e8400#048400#008404\
#00840d#008417#008420#008429#008433#00843c#008445#00844f#008458#008461\
#00846a#008474#00847d#008284#007984#007084#006684#005d84#005484#004a84\
#004184#003884#002e84#002584#001c84#001284#000984#000084#080084#120084\
#1b0084#240084#2e0084#370084#400084#4a0084#530084#5c0084#660084#6f0084\
#780084#820084#84007e#840074#84006b#840062#840059#84004f
#7a0000#7a0800#7a1100#7a1900#7a2200#7a2a00#7a3300#7a3b00#7a4400#7a4d00\
#7a5500#7a5e00#7a6600#7a6f00#7a7700#737a00#6b7a00#627a00#5a7a00#517a00\
#487a00#407a00#377a00#2f7a00#267a00#1e7a00#157a00#0d7a00#047a00#007a04\
#007a0c#007a15#007a1d#007a26#007a2e#007a37#007a40#007a48#007a51#007a59\
#007a62#007a6a#007a73#00787a#006f7a#00677a#005e7a#00557a#004d7a#00447a\
#003c7a#00337a#002b7a#00227a#001a7a#00117a#00087a#00007a#08007a#10007a\
#19007a#21007a#2a007a#33007a#3b007a#44007a#4c007a#55007a#5d007a#66007a\
#6f007a#77007a#7a0074#7a006b#7a0062#7a005a#7a0051#7a0049
#6f0000#6f0700#6f0f00#6f1700#6f1f00#6f2700#6f2e00#6f3600#6f3e00#6f4600\
#6f4e00#6f5500#6f5d00#6f6500#6f6d00#696f00#616f00#596f00#526f00#4a6f00\
#426f00#3a6f00#326f00#2b6f00#236f00#1b6f00#136f00#0b6f00#046f00#006f03\
#006f0b#006f13#006f1b#006f23#006f2a#006f32#006f3a#006f42#006f4a#006f51\
#006f59#006f61#006f69#006d6f#00656f#005e6f#00566f#004e6f#00466f#003e6f\
#00366f#002f6f#00276f#001f6f#00176f#000f6f#00086f#00006f#07006f#0f006f\
#17006f#1e006f#26006f#2e006f#36006f#3e006f#46006f#4d006f#55006f#5d006f\
#65006f#6d006f#6f0069#6f0062#6f005a#6f0052#6f004a#6f0042
#640000#640700#640e00#641500#641c00#642300#642a00#643100#643800#643f00\
#644600#644d00#645400#645b00#646200#5f6400#586400#516400#4a6400#436400\
#3c6400#356400#2e6400#266400#1f6400#186400#116400#0a6400#036400#006403\
#00640a#006411#006418#00641f#006426#00642d#006434#00643b#006442#006449\
#006451#006458#00645f#006364#005c64#005464#004d64#004664#003f64#003864\
#003164#002a64#002364#001c64#001564#000e64#000764#000064#060064#0d0064\
#140064#1b0064#230064#2a0064#310064#380064#3f0064#460064#4d0064#540064\
#5b0064#620064#64005f#640058#640051#64004a#640043#64003c
#590000#590600#590c00#591200#591900#591f00#592500#592c00#593200#593800\
#593f00#594500#594b00#595100#595800#555900#4e5900#485900#425900#3c5900\
#355900#2f5900#295900#225900#1c5900#165900#0f5900#095900#035900#005903\
#005909#00590f#005915#00591c#005922#005928#00592f#005935#00593b#005942\
#005948#00594e#005955#005859#005259#004b59#004559#003f59#003859#003259\
#002c59#002659#001f59#001959#001359#000c59#000659#000059#060059#0c0059\
#120059#180059#1f0059#250059#2b0059#320059#380059#3e0059#450059#4b0059\
#510059#580059#590055#59004f#590048#590042#59003c#590035
#4f0000#4f0500#4f0b00#4f1000#4f1600#4f1b00#4f2100#4f2600#4f2c00#4f3100\
#4f3700#4f3d00#4f4200#4f4800#4f4d00#4b4f00#454f00#3f4f00#3a4f00#344f00\
#2f4f00#294f00#244f00#1e4f00#194f00#134f00#0d4f00#084f00#024f00#004f02\
#004f08#004f0d#004f13#004f18#004f1e#004f23#004f29#004f2f#004f34#004f3a\
#004f3f#004f45#004f4a#004d4f#00484f#00424f#003d4f#00374f#00324f#002c4f\
#00274f#00214f#001b4f#00164f#00104f#000b4f#00054f#00004f#05004f#0a004f\
#10004f#16004f#1b004f#21004f#26004f#2c004f#31004f#37004f#3c004f#42004f\
#47004f#4d004f#4f004b#4f0045#4f0040#4f003a#4f0035#4f002f
#440000#440400#440900#440e00#441300#441800#441c00#442100#442600#442b00\
#443000#443400#443900#443e00#444300#404400#3c4400#374400#324400#2d4400\
#284400#244400#1f4400#1a4400#154400#104400#0c4400#074400#024400#004402\
#004407#00440b#004410#004415#00441a#00441f#004423#004428#00442d#004432\
#004437#00443b#004440#004344#003e44#003944#003444#003044#002b44#002644\
#002144#001c44#001844#001344#000e44#000944#000444#000044#040044#090044\
#0e0044#130044#170044#1c0044#210044#260044#2b0044#2f0044#340044#390044\
#3e0044#430044#440041#44003c#440037#440032#44002d#440029
#390000#390400#390800#390c00#391000#391400#391800#391c00#392000#392400\
#392800#392c00#393000#393400#393800#363900#323900#2e3900#2a3900#263900\
#223900#1e3900#1a3900#163900#123900#0e3900#0a3900#063900#023900#003901\
#003905#00390a#00390e#003912#003916#00391a#00391e#003922#003926#00392a\
#00392e#003932#003936#003839#003439#003039#002c39#002839#002439#002039\
#001c39#001839#001439#001039#000c39#000839#000439#000039#030039#070039\
#0b0039#100039#140039#180039#1c0039#200039#240039#280039#2c0039#300039\
#340039#380039#390036#390032#39002e#39002a#390026#390022
#2e0000#2e0300#2e0600#2e0900#2e0d00#2e1000#2e1300#2e1700#2e1a00#2e1d00\
#2e2000#2e2400#2e2700#2e2a00#2e2e00#2c2e00#292e00#252e00#222e00#1f2e00\
#1c2e00#182e00#152e00#122e00#0e2e00#0b2e00#082e00#052e00#012e00#002e01\
#002e04#002e08#002e0b#002e0e#002e12#002e15#002e18#002e1b#002e1f#002e22\
#002e25#002e29#002e2c#002e2e#002a2e#00272e#00242e#00212e#001d2e#001a2e\
#00172e#00132e#00102e#000d2e#000a2e#00062e#00032e#00002e#03002e#06002e\
#09002e#0d002e#10002e#13002e#16002e#1a002e#1d002e#20002e#24002e#27002e\
#2a002e#2d002e#2e002c#2e0029#2e0026#2e0022#2e001f#2e001c
#240000#240200#240500#240700#240a00#240c00#240f00#241100#241400#241600\
#241900#241b00#241e00#242100#242300#222400#1f2400#1d2400#1a2400#182400\
#152400#132400#102400#0e2400#0b2400#082400#062400#032400#012400#002401\
#002403#002406#002408#00240b#00240d#002410#002413#002415#002418#00241a\
#00241d#00241f#002422#002324#002124#001e24#001c24#001924#001624#001424\
#001124#000f24#000c24#000a24#000724#000524#000224#000024#020024#040024\
#070024#0a0024#0c0024#0f0024#110024#140024#160024#190024#1b0024#1e0024\
#200024#230024#240022#24001f#24001d#24001a#240018#240015
#190000#190100#190300#190500#190700#190800#190a00#190c00#190e00#191000\
#191100#191300#191500#191700#191900#181900#161900#141900#121900#111900\
#0f1900#0d1900#0b1900#091900#081900#061900#041900#021900#001900#001900\
#001902#001904#001906#001908#001909#00190b#00190d#00190f#001910#001912\
#001914#001916#001918#001919#001719#001519#001319#001119#001019#000e19\
#000c19#000a19#000919#000719#000519#000319#000119#000019#010019#030019\
#050019#070019#080019#0a0019#0c0019#0e0019#100019#110019#130019#150019\
#170019#180019#190018#190016#190014#190012#190011#19000f
"""
# raise Exception(CHART_TRUE)

CHART_256 = """
brown__   dark_red_   dark_magenta_   dark_blue_   dark_cyan_   dark_green_
yellow_   light_red   light_magenta   light_blue   light_cyan   light_green

              #00f#06f#08f#0af#0df#0ff        black_______    dark_gray___
            #60f#00d#06d#08d#0ad#0dd#0fd        light_gray__    white_______
          #80f#60d#00a#06a#08a#0aa#0da#0fa
        #a0f#80d#60a#008#068#088#0a8#0d8#0f8
      #d0f#a0d#80d#608#006#066#086#0a6#0d6#0f6
    #f0f#d0d#a0a#808#606#000#060#080#0a0#0d0#0f0#0f6#0f8#0fa#0fd#0ff
      #f0d#d0a#a08#806#600#660#680#6a0#6d0#6f0#6f6#6f8#6fa#6fd#6ff#0df
        #f0a#d08#a06#800#860#880#8a0#8d0#8f0#8f6#8f8#8fa#8fd#8ff#6df#0af
          #f08#d06#a00#a60#a80#aa0#ad0#af0#af6#af8#afa#afd#aff#8df#6af#08f
            #f06#d00#d60#d80#da0#dd0#df0#df6#df8#dfa#dfd#dff#adf#8af#68f#06f
              #f00#f60#f80#fa0#fd0#ff0#ff6#ff8#ffa#ffd#fff#ddf#aaf#88f#66f#00f
                                    #fd0#fd6#fd8#fda#fdd#fdf#daf#a8f#86f#60f
      #66d#68d#6ad#6dd                #fa0#fa6#fa8#faa#fad#faf#d8f#a6f#80f
    #86d#66a#68a#6aa#6da                #f80#f86#f88#f8a#f8d#f8f#d6f#a0f
  #a6d#86a#668#688#6a8#6d8                #f60#f66#f68#f6a#f6d#f6f#d0f
#d6d#a6a#868#666#686#6a6#6d6#6d8#6da#6dd    #f00#f06#f08#f0a#f0d#f0f
  #d6a#a68#866#886#8a6#8d6#8d8#8da#8dd#6ad
    #d68#a66#a86#aa6#ad6#ad8#ada#add#8ad#68d
      #d66#d86#da6#dd6#dd8#dda#ddd#aad#88d#66d        g78_g82_g85_g89_g93_g100
                    #da6#da8#daa#dad#a8d#86d        g52_g58_g62_g66_g70_g74_
      #88a#8aa        #d86#d88#d8a#d8d#a6d        g27_g31_g35_g38_g42_g46_g50_
    #a8a#888#8a8#8aa    #d66#d68#d6a#d6d        g0__g3__g7__g11_g15_g19_g23_
      #a88#aa8#aaa#88a
            #a88#a8a
"""

CHART_88 = """
brown__   dark_red_   dark_magenta_   dark_blue_   dark_cyan_   dark_green_
yellow_   light_red   light_magenta   light_blue   light_cyan   light_green

      #00f#08f#0cf#0ff            black_______    dark_gray___
    #80f#00c#08c#0cc#0fc            light_gray__    white_______
  #c0f#80c#008#088#0c8#0f8
#f0f#c0c#808#000#080#0c0#0f0#0f8#0fc#0ff            #88c#8cc
  #f0c#c08#800#880#8c0#8f0#8f8#8fc#8ff#0cf        #c8c#888#8c8#8cc
    #f08#c00#c80#cc0#cf0#cf8#cfc#cff#8cf#08f        #c88#cc8#ccc#88c
      #f00#f80#fc0#ff0#ff8#ffc#fff#ccf#88f#00f            #c88#c8c
                    #fc0#fc8#fcc#fcf#c8f#80f
                      #f80#f88#f8c#f8f#c0f        g62_g74_g82_g89_g100
                        #f00#f08#f0c#f0f        g0__g19_g35_g46_g52
"""

CHART_16 = """
brown__   dark_red_   dark_magenta_   dark_blue_   dark_cyan_   dark_green_
yellow_   light_red   light_magenta   light_blue   light_cyan   light_green

black_______    dark_gray___    light_gray__    white_______
"""

ATTR_RE = re.compile("(?P<whitespace>[ \n]*)(?P<entry>(?:#[0-9A-Fa-f]{6})|(?:#[0-9A-Fa-f]{3})|(?:[^ \n]+))")
LONG_ATTR = 7
SHORT_ATTR = 4  # length of short high-colour descriptions which may
# be packed one after the next


def parse_chart(chart, convert):
    """
    Convert string chart into text markup with the correct attributes.

    chart -- palette chart as a string
    convert -- function that converts a single palette entry to an
        (attr, text) tuple, or None if no match is found
    """
    out = []
    for match in ATTR_RE.finditer(chart):
        if match.group("whitespace"):
            out.append(match.group("whitespace"))
        entry = match.group("entry")
        entry = entry.replace("_", " ")
        while entry:
            if chart == CHART_TRUE and len(entry) == LONG_ATTR:
                attrtext = convert(entry[:LONG_ATTR])
                elen = LONG_ATTR
            else:
                elen = SHORT_ATTR
                attrtext = convert(entry[:SHORT_ATTR])
            # try the first four characters
            if attrtext:
                entry = entry[elen:].strip()
            else:  # try the whole thing
                attrtext = convert(entry.strip())
                assert attrtext, f"Invalid palette entry: {entry!r}"  # noqa: S101  # "assert" is ok for examples
                elen = len(entry)
                entry = ""
            attr, text = attrtext
            if chart == CHART_TRUE:
                out.append((attr, "\u2584"))
            else:
                out.append((attr, text.ljust(elen)))
    return out


def foreground_chart(chart, background, colors):
    """
    Create text markup for a foreground colour chart

    chart -- palette chart as string
    background -- colour to use for background of chart
    colors -- number of colors (88 or 256)
    """

    def convert_foreground(entry):
        try:
            attr = urwid.AttrSpec(entry, background, colors)
        except urwid.AttrSpecError:
            return None
        return attr, entry

    return parse_chart(chart, convert_foreground)


def background_chart(chart, foreground, colors):
    """
    Create text markup for a background colour chart

    chart -- palette chart as string
    foreground -- colour to use for foreground of chart
    colors -- number of colors (88 or 256)

    This will remap 8 <= colour < 16 to high-colour versions
    in the hopes of greater compatibility
    """

    def convert_background(entry):
        try:
            attr = urwid.AttrSpec(foreground, entry, colors)
        except urwid.AttrSpecError:
            return None
        # fix 8 <= colour < 16
        if colors > 16 and attr.background_basic and attr.background_number >= 8:
            # use high-colour with same number
            entry = "h%d" % attr.background_number
            attr = urwid.AttrSpec(foreground, entry, colors)
        return attr, entry

    return parse_chart(chart, convert_background)


def main():
    palette = [
        ("header", "black,underline", "light gray", "standout,underline", "black,underline", "#88a"),
        ("panel", "light gray", "dark blue", "", "#ffd", "#00a"),
        ("focus", "light gray", "dark cyan", "standout", "#ff8", "#806"),
    ]

    screen = urwid.raw_display.Screen()
    screen.register_palette(palette)

    lb = urwid.SimpleListWalker([])
    chart_offset = None  # offset of chart in lb list

    mode_radio_buttons = []
    chart_radio_buttons = []

    def fcs(widget):
        # wrap widgets that can take focus
        return urwid.AttrMap(widget, None, "focus")

    def set_mode(colors, is_foreground_chart):
        # set terminal mode and redraw chart
        screen.set_terminal_properties(colors)
        screen.reset_default_terminal_palette()

        chart_fn = (background_chart, foreground_chart)[is_foreground_chart]
        if colors == 1:
            lb[chart_offset] = urwid.Divider()
        else:
            chart = {16: CHART_16, 88: CHART_88, 256: CHART_256, 2**24: CHART_TRUE}[colors]
            txt = chart_fn(chart, "default", colors)
            lb[chart_offset] = urwid.Text(txt, wrap="clip")

    def on_mode_change(rb, state, colors):
        # if this radio button is checked
        if state:
            is_foreground_chart = chart_radio_buttons[0].state
            set_mode(colors, is_foreground_chart)

    def mode_rb(text, colors, state=False):
        # mode radio buttons
        rb = urwid.RadioButton(mode_radio_buttons, text, state)
        urwid.connect_signal(rb, "change", on_mode_change, colors)
        return fcs(rb)

    def on_chart_change(rb, state):
        # handle foreground check box state change
        set_mode(screen.colors, state)

    def click_exit(button):
        raise urwid.ExitMainLoop()

    lb.extend(
        [
            urwid.AttrMap(urwid.Text("Urwid Palette Test"), "header"),
            urwid.AttrMap(
                urwid.Columns(
                    [
                        urwid.Pile(
                            [
                                mode_rb("Monochrome", 1),
                                mode_rb("16-Color", 16, True),
                                mode_rb("88-Color", 88),
                                mode_rb("256-Color", 256),
                                mode_rb("24-bit Color", 2**24),
                            ]
                        ),
                        urwid.Pile(
                            [
                                fcs(urwid.RadioButton(chart_radio_buttons, "Foreground Colors", True, on_chart_change)),
                                fcs(urwid.RadioButton(chart_radio_buttons, "Background Colors")),
                                urwid.Divider(),
                                fcs(urwid.Button("Exit", click_exit)),
                            ]
                        ),
                    ]
                ),
                "panel",
            ),
        ]
    )

    chart_offset = len(lb)
    lb.extend([urwid.Divider()])  # placeholder for the chart

    set_mode(16, True)  # displays the chart

    def unhandled_input(key):
        if key in ("Q", "q", "esc"):
            raise urwid.ExitMainLoop()

    urwid.MainLoop(urwid.ListBox(lb), screen=screen, unhandled_input=unhandled_input).run()


if __name__ == "__main__":
    main()
