(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.03eac501842a890f.js","sha256":"03eac501842a890fb0622e9ac4dc446e444559d4a283438f6128bc716a25714d","count":2213,"publishedAt":"2026-10-07T13:35:07Z","state":"calendar-state.json","stateSha256":"39c64c34204e6a72e63805a3fe6cd108c5c4c807406749e4c5920690a470cc2f","sourceState":"calendar-source-state.json","sourceStateSha256":"2461849f1c5cc2416ffcb30a959e30a185c2faffa99a78819ebc82431a2ec622"});
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
