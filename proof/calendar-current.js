(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.631f7f291d43c1a6.js","sha256":"631f7f291d43c1a61b7dfba4a91270b7bd15cfa5de712eabc77b77520050ab31","count":2081,"publishedAt":"2026-10-20T19:22:34Z","state":"calendar-state.json","stateSha256":"07dd2167e472afd7c9fa7e9ab3b6320786305a8cc1b1b44e99cc3a87e8a46377","sourceState":"calendar-source-state.json","sourceStateSha256":"4da32936030bd50614fb922469724f9143c899ce09c23dd747b001648302e861"});
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
