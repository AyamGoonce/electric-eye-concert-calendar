(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.fa1f666be0ae78bd.js","sha256":"fa1f666be0ae78bddf976256e588e69d7d70f4a5fadb5e1ad0c7d03688dba55c","count":2141,"publishedAt":"2026-09-29T18:07:33Z","state":"calendar-state.json","stateSha256":"59ac5176d3f6f83ddf1d0de33b60955c9a4b1891274597128dac7c48aa989310","sourceState":"calendar-source-state.json","sourceStateSha256":"484db5aa632d775aefe651ba43f8afbc3904039f1572272124feb80844feb1f9"});
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
