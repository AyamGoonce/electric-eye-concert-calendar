(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.87d5401402ce00c5.js","sha256":"87d5401402ce00c57319ceaf4bad8243e0a285ecd334d426d10a724908a7e26b","count":2102,"publishedAt":"2026-10-23T17:16:09Z","state":"calendar-state.json","stateSha256":"82fc25fe974a0232657d159a7b2e876922b85a819aef3a6801e659c2375e7ed5","sourceState":"calendar-source-state.json","sourceStateSha256":"496704909103bea05a91f8568bce58d0ffe1ad863c384dd08ba5ff0839ce86af"});
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
