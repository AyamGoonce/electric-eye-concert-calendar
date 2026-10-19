(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.922e1e07f09a7e70.js","sha256":"922e1e07f09a7e709ab73097be83874ce822f65b3c0da2670bc9105a408573bd","count":2072,"publishedAt":"2026-10-19T20:38:26Z","state":"calendar-state.json","stateSha256":"bad278d57aaf6e50b2ed5e8859929879375ff6080b914ef2c2941eaef9f7fd7f","sourceState":"calendar-source-state.json","sourceStateSha256":"eb74859a7dcfcf52e56170ba54bada2749097e214ebddcf8184a266279e8c997"});
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
