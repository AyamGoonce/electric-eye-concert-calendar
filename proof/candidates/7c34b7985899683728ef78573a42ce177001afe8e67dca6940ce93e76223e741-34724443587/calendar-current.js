(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.7c34b79858996837.js","sha256":"7c34b7985899683728ef78573a42ce177001afe8e67dca6940ce93e76223e741","count":2472,"publishedAt":"2026-09-12T23:08:31Z","state":"calendar-state.json","stateSha256":"a42078ee451a2f6fed82f2a92994f05442e5c1e58f00bf891c588ad9afaf33be"});
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
