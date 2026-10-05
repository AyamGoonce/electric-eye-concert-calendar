(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.e9e11d6762d8510e.js","sha256":"e9e11d6762d8510e1ec29c2d46be35a36ca385780c747e4e50051939ccb05769","count":2174,"publishedAt":"2026-10-05T05:51:42Z","state":"calendar-state.json","stateSha256":"cee06cda0264f25cf76a4e62194e2c9b01fd51a7298e4ca050fff9dbf466cb95","sourceState":"calendar-source-state.json","sourceStateSha256":"5b470b31ef422abad0815c5e3f2411fad03c7a5873e4d2e10a8a1a2daa3ad332"});
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
