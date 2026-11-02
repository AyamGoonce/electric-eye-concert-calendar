(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.d1c7aed4f3c72ff4.js","sha256":"d1c7aed4f3c72ff4f8cae9a87f7b8d05c5912a68035d6bd147b25d18d6e0dcff","count":2033,"publishedAt":"2026-11-02T11:23:30Z","state":"calendar-state.json","stateSha256":"cbd9cacbccc85e409d3ec08ad93d84b850941c389a8237df10e8052d608d2bfe","sourceState":"calendar-source-state.json","sourceStateSha256":"50e92e5bdc587f453161cc3832774db398422b9f27ec0f9d309aaa98aa811423"});
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
