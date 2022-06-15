import React from 'react';
import { ProgressIndicator, Stack } from '@fluentui/react';
import { ResourceContextMenu } from '../shared/ResourceContextMenu';
import { ComponentAction, Resource, ResourceUpdate } from '../../models/resource';
import { StatusBadge } from './StatusBadge';

interface ResourceHeaderProps {
  resource: Resource,
  latestUpdate: ResourceUpdate
}

export const ResourceHeader: React.FunctionComponent<ResourceHeaderProps> = (props: ResourceHeaderProps) => {

  return (
    <>
      {props.resource && props.resource.id &&
        <div className="tre-panel">
          <Stack>
            <Stack.Item style={{ borderBottom: '1px #999 solid' }}>
              <Stack horizontal>
                <Stack.Item grow={1}>
                  <h1 style={{ margin: 0, paddingBottom: 10 }}>
                    <span style={{ textTransform: 'capitalize' }}>{props.resource.resourceType.replace('-', ' ')}</span>: {props.resource.properties?.display_name}
                  </h1>
                </Stack.Item>
                {
                  (props.latestUpdate.operation || props.resource.deploymentStatus) &&
                  <Stack.Item>
                    <StatusBadge status={props.latestUpdate.operation ? props.latestUpdate.operation?.status : props.resource.deploymentStatus} />
                  </Stack.Item>
                }
              </Stack>
            </Stack.Item>
            <Stack.Item>
              <ResourceContextMenu resource={props.resource} commandBar={true} componentAction={props.latestUpdate.componentAction} />
            </Stack.Item>
            {
              props.latestUpdate.componentAction === ComponentAction.Lock &&
              <Stack.Item>
                <ProgressIndicator description="Resource locked while it updates" />
              </Stack.Item>
            }
          </Stack>
        </div>
      }
    </>
  );
};
