(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.794cdee5a2b81853.js","sha256":"794cdee5a2b818534f50a88878416e5b1bb36bc5b34229a4fdb02ff3e917f396","count":2070,"publishedAt":"2026-09-27T05:24:29Z","state":"calendar-state.json","stateSha256":"5587b3461bdf6070ff64d347b46f2a974a1c05a7acfd5885e49c28c39c908ca5","sourceState":"calendar-source-state.json","sourceStateSha256":"4fd149f70bee32913af9b043c6b2cfd65371564559dd2223842ec0b2f9a89aa6"});
  var currentSource = document.currentScript && document.currentScript.src;
  window.ElectricEyeConcertManifest = manifest;
  document.dispatchEvent(new CustomEvent("ee:concert-manifest-ready", {detail:manifest}));
  var script = document.createElement("script");
  script.src = new URL(manifest.data, currentSource || window.location.href).href;
  script.onerror = function(){
    document.dispatchEvent(new CustomEvent("ee:concert-data-error", {detail:{reason:"data asset unavailable"}}));
  };
  document.head.appendChild(script);
}());
